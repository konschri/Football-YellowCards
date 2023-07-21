from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity
from factor_analyzer.factor_analyzer import calculate_kmo
from factor_analyzer import FactorAnalyzer
from sklearn.decomposition import PCA
from sklearn import preprocessing
import matplotlib.pyplot as plt
import pandas as pd



class Analyzer:
    
    @staticmethod
    def principalcomponentsanalysis(TrainDF: pd.DataFrame, 
                                    TestDF: pd.DataFrame, 
                                    explained_variance_threshold: float = 0.7):
        
        # Keep the target variable out of analysis and scale the data
        train_target, test_target = TrainDF["Target"], TestDF["Target"]
        TrainDF = preprocessing.scale(TrainDF.drop(["Target"], axis=1))
        TestDF = preprocessing.scale(TestDF.drop(["Target"], axis=1))
        
        # Perform default pca in order to decide the number of components. The threshold of cummulative explained
        # variance is given as input to the method
        epca = PCA()
        epca.fit(TrainDF)
        
        no_of_components = 0
        variance_sum = 0
        for var in epca.explained_variance_ratio_:
            variance_sum += var
            no_of_components += 1
            if variance_sum >= explained_variance_threshold:
                break
        
        # After computing the no_of_components perform a specific PCA transformation
        # on both Train and Test data
        pca = PCA(n_components=no_of_components)
        train_results_array = pca.fit_transform(TrainDF)
        test_results_array = pca.transform(TestDF)
        
        train_result = pd.DataFrame(train_results_array)
        test_result = pd.DataFrame(test_results_array)
        
        # Add the isolated target variable to the transformed data
        train_result["Target"] = train_target
        test_result["Target"] = test_target
        
        return train_result, test_result
    
    
    @staticmethod
    def factoranalysis(TrainDF: pd.DataFrame, 
                       TestDF: pd.DataFrame, 
                       rotation: str = None, 
                       eigenvalue_threshold: float = 1.0):
        
        # Keep the target variable out of analysis and scale the data
        train_target, test_target = TrainDF["Target"], TestDF["Target"]
        TrainDF = preprocessing.scale(TrainDF.drop(["Target"], axis=1))
        TestDF = preprocessing.scale(TestDF.drop(["Target"], axis=1))
        
        # Perform the necessary tests to ensure that data are suitable for factor analysis
        print("Performing Adequacy Test ...")
        print("First checking Barlett's Test.")
        chi_square_value, p_value = calculate_bartlett_sphericity(TrainDF)
        if p_value < 0.05:
            print(f"p-value = {p_value}. The test was statistically significant, indicating that the observed correlation matrix is not the identity matrix")
        else:
            print(f"p-value = {p_value} The particular dataset is not appropriate for factor analysis")
            return ""
        
        print("Performing Kaiser-Meyer-Olkin Test ...")
        kmo_all, kmo_model = calculate_kmo(TrainDF)
        if kmo_model > 0.6:
            print(f"kmo-statistic = {round(kmo_model, 3)}. The particular dataset is adequate")
        else:
            print(f"kmo-statistic = {round(kmo_model, 3)}. The particular dataset is considered inadequate")
            return ""
        
        # Perform default efa in order to decide the number of factors. The threshold of eigenvectors to keep
        # is given as input to the method
        efa = FactorAnalyzer(rotation=rotation)
        efa.fit(TrainDF)
        
        ev, v = efa.get_eigenvalues()

        
        # Create scree plot using matplotlib
        plt.scatter(range(1, TrainDF.shape[1]+1), ev)
        plt.plot(range(1, TrainDF.shape[1]+1), ev)
        plt.title('Scree Plot')
        plt.xlabel('Factors')
        plt.ylabel('Eigenvalue')
        plt.grid()
        plt.show()
        
        # After computing the no_of_factors perform a specific FA transformation
        # on both Train and Test data
        no_of_factors = sum(i > eigenvalue_threshold for i in ev)
        print(f"The analysis resulted in {no_of_factors} factors.")
        fa = FactorAnalyzer(n_factors=no_of_factors, rotation=rotation)
        fa.fit(TrainDF)
        
        # Add the isolated target variable to the transformed data
        train_results_array = fa.transform(TrainDF)
        train_result = pd.DataFrame(train_results_array)
        train_result["Target"] = train_target
        
        test_results_array = fa.transform(TestDF)
        test_result = pd.DataFrame(test_results_array)
        test_result["Target"] = test_target
        
        return train_result, test_result
