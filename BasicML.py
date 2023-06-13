from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import numpy as np

class MLPipeline:
    
    def __init__(self, data, reds=False, scale=True, splitSize=0.2, plot=True):
        self.data = data
        self.reds = reds
        self.scale = scale
        self.splitSize = splitSize
        self.plot = plot
        if self.reds:
            self.data.drop(["Yellows"], axis=1, inplace=True)
            self.Y = self.data["Reds"]
            self.X = self.data.drop(["Reds"], axis=1)
            self.baselineValue = 0.25
        else:
            self.data.drop(["Reds"], axis=1, inplace=True)
            self.Y = self.data["Yellows"]
            self.X = self.data.drop(["Yellows"], axis=1)
            self.baselineValue = 5
   
    
    def run(self):
        self.split()
        if self.scale:
            self.scaleMethod()
        self.createModel()
        self.results(self.plot)
        
    
    def split(self):
        self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(self.X, self.Y, test_size=self.splitSize, random_state=42)
    
    def scaleMethod(self):
        scaler = StandardScaler()
        self.X_train = scaler.fit_transform(self.X_train)
        self.X_test = scaler.transform(self.X_test)
        
    def createModel(self):
        clf = RandomForestRegressor(random_state=9)
        
        param_grid = {
                    "n_estimators" : [50, 100, 200, 300],
                    "max_depth" : [2, 3, 5]
                     }
        
        self.grid = GridSearchCV(estimator=clf, param_grid=param_grid, n_jobs=-1, verbose=2, cv=5)
        self.grid.fit(self.X_train, self.Y_train)
    
    def results(self, plot):
        print(self.grid.best_estimator_)
        results = self.grid.predict(self.X_test)
        model_mse = mean_squared_error(self.Y_test, results)
        print(f"Trained model: {model_mse}")
        
        baseline = np.repeat(self.baselineValue, len(results))
        baseline_mse = mean_squared_error(self.Y_test, baseline)
        print(f"Baseline model: {baseline_mse}")
        
        if plot:
            x = np.arange(len(self.Y_test))
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(x, results, color="red", label="Model")
            ax.plot(x, self.Y_test, color="green", label="Ground Truth")
            ax.plot(x, baseline, color="blue", label="Baseline")
            
            better_points = [i for i in range(len(self.Y_test)) if baseline[i] < results[i]]
            for i in better_points:
                plt.scatter(i, baseline[i], color='black', marker='o', s=20)  # Marker for baseline
                # plt.annotate('Baseline Better', (i, baseline[i]), textcoords='offset points', xytext=(0, 10), ha='center')
            
            
            ax.set_xlabel("Data Point")
            ax.set_ylabel("Value")
            ax.legend()
            plt.show()
        