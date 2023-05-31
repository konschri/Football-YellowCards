from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import numpy as np

class MLPipeline():
    
    def __init__(self, data, reds=False):
        self.data = data
        self.reds = reds
        if self.reds:
            self.data.drop(["Yellows"], axis=1, inplace=True)
            self.Y = self.data["Reds"]
            self.X = self.data.drop(["Reds"], axis=1)
        else:
            self.data.drop(["Reds"], axis=1, inplace=True)
            self.Y = self.data["Yellows"]
            self.X = self.data.drop(["Yellows"], axis=1)
   
        
    def split(self):
        self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(self.X, self.Y, test_size=0.2, random_state=42)
    
    def scale(self):
        scaler = StandardScaler()
        self.X_train = scaler.fit_transform(self.X_train)
        self.X_test = scaler.transform(self.X_test)
        
    def predict(self):
        clf = RandomForestRegressor(random_state=9)
        
        param_grid = {
                    "n_estimators" : [50, 100, 200, 300],
                    "max_depth" : [2, 3, 5]
                     }
        
        self.grid = GridSearchCV(estimator=clf, param_grid=param_grid, n_jobs=-1, verbose=2, cv=5)
        self.grid.fit(self.X_train, self.Y_train)
    
    def results(self):
        print(self.grid.best_estimator_)
        results = self.grid.predict(self.X_test)
        model_mse = mean_squared_error(self.Y_test, results)
        print(type(model_mse))
        
        baseline = np.repeat(5, len(results))
        baseline_mse = mean_squared_error(self.Y_test, baseline)
        print(type(baseline_mse))