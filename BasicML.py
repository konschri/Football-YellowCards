from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from sklearn.inspection import permutation_importance
import matplotlib.pyplot as plt
import numpy as np

class MLPipeline:
    
    def __init__(self, data, testData, scale=True, algorithm="randomforest"):
        self.data = data
        self.testData= testData
        self.scale = scale
        self.algorithm = algorithm
        # self.splitSize = splitSize
        # self.plot = plot
        
        
        self.targetTransformationDict = {
                "ZeroToTwo": [0, 1, 2],
                "ThreeOrFour": [3, 4],
                "FiveOrSix": [5, 6],
                "SevenOrMore": list(range(7, 20))}
        
        self.data["Target"] = self.data["Yellows"].apply(lambda x: next((k for k, v in self.targetTransformationDict.items() if x in v), None))
        self.testData["Target"] = self.testData["Yellows"].apply(lambda x: next((k for k, v in self.targetTransformationDict.items() if x in v), None))
        
        self.data.drop(["Yellows", "Reds"], axis=1, inplace=True)
        self.testData.drop(["Yellows", "Reds"], axis=1, inplace=True)
        
        self.Y = self.data["Target"]
        self.X = self.data.drop(["Target"], axis=1)
        
        self.Y_test = self.testData["Target"]
        self.X_test = self.testData.drop(["Target"], axis=1)
    
    
    def run(self):
        
        if self.scale:
            self.scaleMethod()
        if self.algorithm == "randomforest":
            print("The selected algorithm is Random Forest ... please wait!")
            self.classification_rf()
        else:
            print("The selected algorithm is Logistic Regression ... please wait!")
            self.classification_lr()
        

    def scaleMethod(self):
        scaler = StandardScaler()
        self.X = scaler.fit_transform(self.X)
        self.X_test = scaler.transform(self.X_test)
        
    
    def classification_rf(self):
        clf = RandomForestClassifier(random_state=42)

        param_grid = {
                    "n_estimators" : [100, 300, 400],
                    "max_depth" : [3, 5, 6],
                    "max_features": [5, 6, 7]
                      }
        
        self.grid = GridSearchCV(estimator=clf, param_grid=param_grid, n_jobs=-1, verbose=2, cv=5)
        self.grid.fit(self.X, self.Y)
        
        
        print(f"The best parameters combination was {self.grid.best_estimator_}")
        
        best_model = self.grid.best_estimator_
        
        
        best_accuracy = self.grid.best_score_
        print(f"The predicted accuracy on validation set is : {round(best_accuracy, 3)}")
        
        results = best_model.predict(self.X_test)
        
        test_accuracy = accuracy_score(self.Y_test, results)
        print(f"The predicted accuracy on test set is {round(test_accuracy, 3)}")
        
        # self.baselineValue = max(self.Y, key=self.Y.count)
        baselineValue = np.argmax(np.argmax(self.Y))
        print(f"The baseline value is: {baselineValue}")
        baseline = np.repeat(baselineValue, len(results))
        baseline_mse = accuracy_score(self.Y_test, baseline)
        
        print(f"Baseline model: {round(baseline_mse, 3)}")
        
        result = permutation_importance(self.grid, self.X, self.Y, n_repeats=10, random_state=42)
        perm_sorted_idx = result.importances_mean.argsort()
        print(f"Permutation results: {perm_sorted_idx}")
        
        for i in perm_sorted_idx:
            
            
            if result.importances_mean[i] - 2 * result.importances_std[i] > 0:
                print(f"{self.data.columns[i]:<8}"
                f"{result.importances_mean[i]:.3f}"
                f" +/- {result.importances_std[i]:.3f}")
    
    def classification_lr(self):

        label_encoder = LabelEncoder()
        self.Y = label_encoder.fit_transform(self.Y)
        print(self.Y[:10])
        self.Y_test = label_encoder.transform(self.Y_test)
        print(self.Y_test[:10])
        
        encoding_scheme = dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_)))
        print("Encoding scheme:", encoding_scheme)
        
        clf = LogisticRegression(max_iter=1000, random_state=42)

        param_grid = {
                    "penalty" : ["l1", "l2"],
                    "C" : [0.1, 0.5, 1],
                    "solver": ["liblinear", "saga"]
                      }
        
        self.grid = GridSearchCV(estimator=clf, param_grid=param_grid, n_jobs=-1, verbose=2, cv=5)
        self.grid.fit(self.X, self.Y)
        
        
        print(f"The best parameters combination was {self.grid.best_estimator_}")
        
        best_model = self.grid.best_estimator_
        
        
        best_accuracy = self.grid.best_score_
        print(f"The predicted accuracy on validation set is : {round(best_accuracy, 3)}")
        
        results = best_model.predict(self.X_test)
        
        test_accuracy = accuracy_score(self.Y_test, results)
        print(f"The predicted accuracy on test set is {round(test_accuracy, 3)}")
        
        # Use as baseline prediction the class with the most occurences in the training dataset
        
        baselineValue = np.argmax(np.argmax(self.Y))
        print(f"The baseline value is: {baselineValue}")
        baseline = np.repeat(baselineValue, len(results))
        baseline_mse = accuracy_score(self.Y_test, baseline)
        
        print(f"Baseline model: {round(baseline_mse, 3)}")
        
        
        
        