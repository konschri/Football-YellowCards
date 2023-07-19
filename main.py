from processing import process
from basicml import MLPipeline
import pandas as pd
import glob

folder_path_details = "datasets\\datasets_details\\"
folder_path_statistics = "datasets\\datasets_statistics\\"


csv_files_details = glob.glob(folder_path_details + "*.csv")
csv_files_statistics = glob.glob(folder_path_statistics + "*.csv")


assert len(csv_files_details) == len(csv_files_statistics)
csv_files = list(zip(csv_files_details, csv_files_statistics))

dataframes = []
# Iterate over each CSV file
for pair in csv_files:
 
    # Process the data according to process class
    seasonInstance = process(pair)  
    
    # Append the resulted dataframe to the list
    dataframes.append(seasonInstance.run())
    

train_df = pd.concat(dataframes[:-1], ignore_index=True)
test_df = dataframes[-1]

# correlation_matrix = train_df.corr()
# print(correlation_matrix)


#%%
""" Perform factor analysis """

def factoranalysis(TrainDF: pd.DataFrame, TestDF: pd.DataFrame, rotation=None, eigenvalue_threshold=0.8):
    from sklearn import preprocessing
    from factor_analyzer import FactorAnalyzer
    from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity
    from factor_analyzer.factor_analyzer import calculate_kmo
    import matplotlib.pyplot as plt
    
    train_target, test_target = TrainDF["Target"], TestDF["Target"]
    TrainDF = preprocessing.scale(TrainDF.drop(["Target"], axis=1))
    TestDF = preprocessing.scale(TestDF.drop(["Target"], axis=1))
    
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
    
    # Create factor analysis object and perform factor analysis
    efa = FactorAnalyzer(rotation=rotation)
    # fa.transform(X, X.shape[1], rotation=rotation)
    efa.fit(TrainDF)
    # Check Eigenvalues
    ev, v = efa.get_eigenvalues()
    print(ev)
    
    # Create scree plot using matplotlib
    plt.scatter(range(1,TrainDF.shape[1]+1),ev)
    plt.plot(range(1,TrainDF.shape[1]+1),ev)
    plt.title('Scree Plot')
    plt.xlabel('Factors')
    plt.ylabel('Eigenvalue')
    plt.grid()
    plt.show()
    
    
    no_of_factors = sum(i > eigenvalue_threshold for i in ev)
    print(f"The analysis resulted in {no_of_factors} factors.")
    fa = FactorAnalyzer(n_factors=no_of_factors, rotation=rotation)
    fa.fit(TrainDF)
    
    train_results_array = fa.transform(TrainDF)
    train_result = pd.DataFrame(train_results_array)
    train_result["Target"] = train_target
    
    test_results_array = fa.transform(TestDF)
    test_result = pd.DataFrame(test_results_array)
    test_result["Target"] = test_target
    
    return train_result, test_result


TrainDF, TestDF = factoranalysis(train_df, test_df)



#%%
pr = MLPipeline(TrainDF, TestDF, algorithm="lr")
pr.run()



