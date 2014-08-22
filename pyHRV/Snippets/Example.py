__author__ = 'AleB'

import pyHRV
import pandas

# We load the data series from a csv file with tabulations as separators
# IBI from the column "IBI"
ibi = pandas.read_csv("RD.txt", sep="\t")["IBI"]
lab = pandas.read_csv("RD.txt", sep="\t")["label"]
# We create the data series specifying the optional field labels
data_series = pyHRV.DataSeries(data=ibi, labels=lab)
# and the windows collection with the linear time windows generator with windows of 30s every 30s.
windows = pyHRV.LinearTimeWinGen(step=20000, width=20000, data=data_series)
# The windows mapper will do all the rest of the work, we just need to put
# there every Time (TD) and Frequency (FD) Domain and every Non Linear Index
mapper = pyHRV.WindowsMapper(
    data_series, windows, pyHRV.indexes.TDIndexes.__all__ +
    pyHRV.indexes.FDIndexes.__all__ +
    pyHRV.indexes.NonLinearIndexes.__all__)
mapper.compute_all()
# We convert the results to a data frame
data_frame = pandas.DataFrame(mapper.results)
# to give it an header
data_frame.columns = mapper.labels
# and to save it in a csv file, without the line number (index)
data_frame.to_csv("results.csv", sep="\t", index=False)
