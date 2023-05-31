"""
test for calling objects
"""

from pre_processing import process
from BasicML import MLPipeline

a = process("SpanishLaLiga17_18.csv")
data1 = a.dataPreprocess()
data2 = a.featureTransformation(1, 4, 7, 18)
    
pr = MLPipeline(data2)