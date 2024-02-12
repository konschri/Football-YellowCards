from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, plot_confusion_matrix, roc_curve, auc
import matplotlib.pyplot as plt
import xgboost as xgb
import pickle


class MLPipeline:
    
    def __init__(self, data, testData, scale=True, algorithm="rf"):
        self.data = data
        self.testData= testData
        self.scale = scale
        self.algorithm = algorithm

        
        self.Y = self.data["Target"]
        self.X = self.data.drop(["Target"], axis=1)
        
        self.Y_test = self.testData["Target"]
        self.X_test = self.testData.drop(["Target"], axis=1)
        
        label_encoder = LabelEncoder()
        self.Y = label_encoder.fit_transform(self.Y)
        self.Y_test = label_encoder.transform(self.Y_test)
        
        self.verbose = 1
        self.cv = 5
        
        encoding_scheme = dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_)))
        print("Encoding scheme:", encoding_scheme)
    
    
    def run(self):
        if self.scale:
            self.scaleMethod()
        if self.algorithm == "rf":
            print("The selected algorithm is Random Forest ... please wait!")
            self.classification_rf()
        elif self.algorithm == "xgb":
            print("The selected algorithm is XGBoost ... please wait!")
            self.classification_xgb() 
        elif self.algorithm == "lr":
            print("The selected algorithm is Logistic Regression ... please wait!")
            self.classification_lr()
        self.scoring()
        

    def scaleMethod(self):
        scaler = StandardScaler()
        self.X = scaler.fit_transform(self.X)
        
        with open('models/scaler.pkl','wb') as f:
            pickle.dump(scaler, f)
        
        
        self.X_test = scaler.transform(self.X_test)
        
    
    def classification_xgb(self):
        clf = xgb.XGBClassifier(objective="binary:logistic", seed=42)
        
        param_grid = {
                    'max_depth': range (2, 10, 1),
                    'n_estimators': range(60, 220, 40),
                    'learning_rate': [0.1, 0.01, 0.05]
                        }

        
        self.grid = GridSearchCV(estimator=clf, param_grid=param_grid, n_jobs=1, verbose=self.verbose, cv=self.cv)
        self.grid.fit(self.X, self.Y)
        
        with open('models/model.pkl','wb') as f:
            pickle.dump(self.grid, f)
        
        print(f"The best parameters combination was {self.grid.best_estimator_}")
        
    
    def classification_rf(self):
        clf = RandomForestClassifier(random_state=42)

        param_grid = {
                    "n_estimators" : [100, 300, 400],
                    "max_depth" : [3, 5, 6],
                    "max_features": [5, 6, 7]
                      }
        
        self.grid = GridSearchCV(estimator=clf, param_grid=param_grid, n_jobs=-1, verbose=self.verbose, cv=self.cv)
        self.grid.fit(self.X, self.Y)
        print(f"The best parameters combination was {self.grid.best_estimator_}")
        
        
    def classification_lr(self):
        clf = LogisticRegression(max_iter=1000, random_state=42)

        param_grid = {
                    "penalty" : ["l1", "l2"],
                    "C" : [0.001, 0.01, 0.1, 0.5, 1],
                    "solver": ["liblinear", "saga"]
                      }
        
        self.grid = GridSearchCV(estimator=clf, param_grid=param_grid, n_jobs=-2, verbose=self.verbose, cv=self.cv)
        self.grid.fit(self.X, self.Y)
        print(f"The best parameters combination was {self.grid.best_estimator_}")
        
        
    def scoring(self):
        
        best_model = self.grid.best_estimator_
        
        best_accuracy = self.grid.best_score_
        print(f"The predicted accuracy on validation set is : {round(best_accuracy, 3)}")
        
        results = best_model.predict(self.X_test)

        
        test_accuracy = accuracy_score(self.Y_test, results)
        print(f"The predicted accuracy on test set is {round(test_accuracy, 3)}")
        
        
        print("Below check the confusion matrix")
        plot_confusion_matrix(self.grid, self.X_test, self.Y_test)
        
        
        y_probabilities = self.grid.predict_proba(self.X_test)
        fpr, tpr, thresholds = roc_curve(self.Y_test, y_probabilities[:, 1])  # Assuming 1 represents the positive class
        roc_auc = auc(fpr, tpr)
        
        
        plt.figure()
        plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = {:.2f})'.format(roc_auc))
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic (ROC) Curve')
        plt.legend(loc="lower right")
        plt.show()
        print("AUC-ROC:", roc_auc)
        
        
        