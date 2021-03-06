# -*- coding: utf-8 -*-
"""SDP-II ML Kısmı.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OVY9fDRNA6MXgJVrfYrSZQ3Q5KW9oWQH

##PRE-PROCESSING

###Increase Data with Network Style Windowing
"""

from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.svm import OneClassSVM
import numpy as np
from sklearn.metrics import classification_report
import pandas as pd
import pickle
import warnings
from imblearn.over_sampling import SMOTE, ADASYN
from sklearn.datasets import fetch_openml
from imblearn.over_sampling import RandomOverSampler
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, DetrendOperations
import brainflow
import os
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.svm import OneClassSVM
import numpy as np
from sklearn.metrics import classification_report
import pandas as pd
import pickle
import warnings
from imblearn.over_sampling import SMOTE, ADASYN
from sklearn.datasets import fetch_openml
from imblearn.over_sampling import RandomOverSampler
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor
warnings.filterwarnings("ignore")

print("I READ DATA")
df = pd.read_csv('temp_data.csv')
removeTransitonIndexes = []
for i in range(0, len(df)):
  if df['Direction'][i] == 'Transition':
    removeTransitonIndexes.append(i)

df1 = df.drop(index = removeTransitonIndexes)
data = df1.reset_index(drop=True)
data = data.drop(range(0, 25))
data = data.reset_index(drop=True)

drop_list_start_index = []
startDir = 'forward'
for i in range(0, len(data['Direction'])):
  currentDir = data['Direction'][i]
  if currentDir != startDir:
    drop_list_start_index.append(i)
    startDir = currentDir

#DROP FIRST 200MS OF EVERY DIRECTIONS DURING TRAINING
for i in drop_list_start_index:
  data = data.drop(range(i, i+25))

data_after200ms = data.reset_index(drop=True)

start_indexes = [0]
startDir = 'forward'
for i in range(0, len(data_after200ms['Direction'])):
  currentDir = data_after200ms['Direction'][i]
  if currentDir != startDir:
    start_indexes.append(i)
    startDir = currentDir
#start_indexes has values for directions' start point.
#forward -> right -> backward -> left -> stop ->... *10(trial number)

channel_names = ['Fp1','Fp2','C3','C4','P7','P8','O1','O2','F7','F8','F3','F4','T7','T8','P3','P4']
channel_numbers = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]

#TO VISIT EVERY CHANGES IN DIRECTION
#THERE ARE 50 CHANGE INDEX
for index in range(0, len(start_indexes)-1):
  getting_dir_chunk = data_after200ms[start_indexes[index] : start_indexes[index+1]]
  getting_dir_chunk = getting_dir_chunk.reset_index(drop=True)

  len_of_current = len(getting_dir_chunk)

  check = not os.path.exists('temp_alphaHigh.csv')
  direction = data_after200ms['Direction'][start_indexes[index]]

  data = getting_dir_chunk
  data = data.iloc[:,:-1]
  data = data.T
  data = data.to_numpy()

  for i in range(125,len_of_current, 5):
    data_list_alpha = []
    data_list_beta = []
    data_list_gamma = []
    data_list_theta = []
    data_list_alphaLow = []
    data_list_betaLow = []
    data_list_gammaLow = []
    data_list_thetaLow = []

    for channel in channel_numbers:
        theta_list = []
        alpha_list = []
        beta_list = []
        gamma_list = []
        thetaLow_list = []
        alphaLow_list = []
        betaLow_list = []
        gammaLow_list = []


        nfft = DataFilter.get_nearest_power_of_two(64)
        psd = DataFilter.get_psd_welch(data[channel][i-125:i], nfft, nfft // 2, 128, brainflow.WindowFunctions.BLACKMAN_HARRIS.value)
        

        band_power_thetaLow = DataFilter.get_band_power(psd, 4.0, 5.5)
        band_power_thetaHigh = DataFilter.get_band_power(psd, 5.5, 7.0)
        band_power_alphaLow = DataFilter.get_band_power(psd, 7.0, 10.0)
        band_power_alphaHigh = DataFilter.get_band_power(psd, 10.0, 13.0)
        band_power_betaLow = DataFilter.get_band_power(psd, 14.0, 22.0)
        band_power_betaHigh = DataFilter.get_band_power(psd, 22.0, 30.0)
        band_power_gammaLow = DataFilter.get_band_power(psd, 31.0, 38.0)
        band_power_gammaHigh = DataFilter.get_band_power(psd, 38.0, 45.0)

        theta_list.append(band_power_thetaHigh)
        alpha_list.append(band_power_alphaHigh)
        beta_list.append(band_power_betaHigh)
        gamma_list.append(band_power_gammaHigh)

        thetaLow_list.append(band_power_thetaLow)
        alphaLow_list.append(band_power_alphaLow)
        betaLow_list.append(band_power_betaLow)
        gammaLow_list.append(band_power_gammaLow)
        

        #High values are assigned
        data_list_theta.append(theta_list)
        data_list_alpha.append(alpha_list)
        data_list_beta.append(beta_list)
        data_list_gamma.append(gamma_list)

        #Low values are assigned
        data_list_thetaLow.append(thetaLow_list)
        data_list_alphaLow.append(alphaLow_list)
        data_list_betaLow.append(betaLow_list)
        data_list_gammaLow.append(gammaLow_list)



    #ALPHAS ARE COLLECTED INSIDE THIS
    df_alpha = pd.DataFrame(data_list_alpha,
                      index=['A_Fp1','A_Fp2','A_C3','A_C4','A_P7','A_P8','A_O1','A_O2','A_F7','A_F8','A_F3','A_F4','A_T7','A_T8','A_P3','A_P4']).T
    df_alpha.to_csv("temp_alphaHigh.csv", mode='a', header=check,index=False)


    # LOW ALPHAS ARE COLLECTED INSIDE THIS
    df_alphaLow = pd.DataFrame(data_list_alphaLow,
                            index=['ALow_Fp1','ALow_Fp2','ALow_C3','ALow_C4','ALow_P7','ALow_P8','ALow_O1','ALow_O2','ALow_F7','ALow_F8','ALow_F3','ALow_F4','ALow_T7','ALow_T8','ALow_P3','ALow_P4']).T
    df_alphaLow.to_csv("temp_alphaLow.csv", mode='a', header=check, index=False)


    # BETAS ARE COLLECTED INSIDE THIS
    df_beta = pd.DataFrame(data_list_beta,
        index=['B_Fp1','B_Fp2','B_C3','B_C4','B_P7','B_P8','B_O1','B_O2','B_F7','B_F8','B_F3','B_F4','B_T7','B_T8','B_P3','B_P4']).T
    df_beta.to_csv("temp_betaHigh.csv", mode='a', header=check,index=False)


    #Low BETA
    df_betaLow = pd.DataFrame(data_list_betaLow,
                            index=['BLow_Fp1','BLow_Fp2','BLow_C3','BLow_C4','BLow_P7','BLow_P8','BLow_O1','BLow_O2','BLow_F7','BLow_F8','BLow_F3','BLow_F4','BLow_T7','BLow_T8','BLow_P3','BLow_P4']).T
    df_betaLow.to_csv("temp_betaLow.csv", mode='a', header=check, index=False)


    #GAMMAS ARE COLLECTED INSIDE THIS
    df_gamma = pd.DataFrame(data_list_gamma,
                            index=['G_Fp1','G_Fp2','G_C3','G_C4','G_P7','G_P8','G_O1','G_O2','G_F7','G_F8','G_F3','G_F4','G_T7','G_T8','G_P3','G_P4']).T
    df_gamma.to_csv("temp_gammaHigh.csv", mode='a', header=check,index=False)

    #LOWGAMMAS ARE COLLECTED INSIDE THIS
    df_gammaLow = pd.DataFrame(data_list_gammaLow,
                            index=['GLow_Fp1','GLow_Fp2','GLow_C3','GLow_C4','GLow_P7','GLow_P8','GLow_O1','GLow_O2','GLow_F7','GLow_F8','GLow_F3','GLow_F4','GLow_T7','GLow_T8','GLow_P3','GLow_P4']).T
    df_gammaLow.to_csv("temp_gammaLow.csv", mode='a', header=check,index=False)


    df_theta = pd.DataFrame(data_list_theta,
                            index=['T_Fp1','T_Fp2','T_C3','T_C4','T_P7','T_P8','T_O1','T_O2','T_F7','T_F8','T_F3','T_F4','T_T7','T_T8','T_P3','T_P4']).T
    df_theta.to_csv("temp_thetaHigh.csv", mode='a', header=check,index=False)

    df_thetaLow = pd.DataFrame(data_list_thetaLow,
                            index=['TLow_Fp1','TLow_Fp2','TLow_C3','TLow_C4','TLow_P7','TLow_P8','TLow_O1','TLow_O2','TLow_F7','TLow_F8','TLow_F3','TLow_F4','TLow_T7','TLow_T8','TLow_P3','TLow_P4']).T
    df_thetaLow['Direction'] = direction
    df_thetaLow.to_csv("temp_thetaLow.csv", mode='a', header=check,index=False)

    if check:
        check = False

"""###Read Files, Outlier Elimination, Oversampling, Windowing"""
dfalpha = pd.read_csv('temp_alphaHigh.csv')
dfalphaLow = pd.read_csv('temp_alphaLow.csv')
dfbeta = pd.read_csv('temp_betaHigh.csv')
dfbetaLow = pd.read_csv('temp_betaLow.csv')
dfgamma = pd.read_csv('temp_gammaHigh.csv')
dfgammaLow = pd.read_csv('temp_gammaLow.csv')
dftheta = pd.read_csv('temp_thetaHigh.csv')
dfthetaLow = pd.read_csv('temp_thetaLow.csv')
frames = [dfalpha, dfalphaLow, dfbeta, dfbetaLow, dfgamma, dfgammaLow, dftheta, dfthetaLow]
df = pd.concat(frames, axis=1)

removeTransitonIndexes = []
for i in range(0, len(df)):
  if df['Direction'][i] == 'Transition':
    removeTransitonIndexes.append(i)
df1 = df.drop(index = removeTransitonIndexes)
df1 = df1.reset_index(drop=True)


start_indexes = [0]
startDir = 'forward'
for i in range(0, len(df1['Direction'])):
  currentDir = df1['Direction'][i]
  if currentDir != startDir:
    start_indexes.append(i)
    startDir = currentDir

df_target = df1['Direction']
df_data = df1.iloc[:, :-1]

print(len(start_indexes))
#It gets last 2 as test
if len(start_indexes) == 49:
    numm = len(start_indexes)-10
elif len(start_indexes) == 74:
    numm = len(start_indexes)-15
else:
    numm = len(start_indexes)-20

print(numm)
Xtest = df_data[start_indexes[numm]:]
ytest = df_target[start_indexes[numm]:]
Xtrain1 = df_data[0:start_indexes[numm]]
ytrain1 = df_target[0:start_indexes[numm]]


clf = OneClassSVM(kernel='rbf', nu=0.55, degree=3)
#Outlier remove inside train
shouldRemove = clf.fit_predict(Xtrain1)
index = 0
temp = []
for x in shouldRemove:
  if x == -1:
    temp.append(index)
  index += 1
Xtrain = np.delete(Xtrain1.values, temp, 0)
ytrain = np.delete(ytrain1.values, temp, 0)


#SMOTE oversampling
sm = SMOTE(sampling_strategy='all')
Xtrain, ytrain = sm.fit_resample(Xtrain, ytrain)



def testFit(model):
  yfit = model.predict(Xtest)
  print("TEST PREDICTION")
  print(classification_report(ytest, yfit,
                            target_names=['forward','right','backward','left','stop']))
  a = confusion_matrix(ytest, yfit)
  sns.heatmap(a.T, square=True, annot=True, fmt='d', cbar=False,
            xticklabels=['forward','right','backward','left','stop'], yticklabels=['forward','right','backward','left','stop'])
  
def trainFit(model):
  print("------------------")
  print("------------------")
  print("------------------")
  print("TRAIN PREDICTION")
  yyfit = model.predict(Xtrain)
  print(classification_report(ytrain, yyfit,
                            target_names=['forward','right','backward','left','stop']))
  
  print("----------")
  print("HEATMAP OF TEST")
  #b = confusion_matrix(ytrain, yyfit)
  #sns.heatmap(b.T, square=True, annot=True, fmt='d', cbar=False,
  #          xticklabels=['forward','right','backward','left','stop'], yticklabels=['forward','right','backward','left','stop'])

def fitting(model):
  model.fit(Xtrain, ytrain)
  testFit(model)
  trainFit(model)


"""##MODELS"""
##########################################################################
model_SVM = make_pipeline(StandardScaler(), SVC(gamma='auto'))
param_grid = {'svc__C': [0.2],
              'svc__gamma': [0.0001],
              'svc__degree': [2],
              'svc__kernel': ["linear"]}
grid = GridSearchCV(model_SVM, param_grid)
print("----------------SVM----------------")
fitting(grid)
print("--------------------------------")
print(grid.best_params_)
##########################################################################
##########################################################################
from sklearn.linear_model import LogisticRegression
model_LR = LogisticRegression()
param_grid = {'penalty': ["l1"],
              'C': [2.0],
              'intercept_scaling': [1.0],
              'solver': ["liblinear"],
              'l1_ratio': [2.0]}
grid1 = GridSearchCV(model_LR, param_grid)
print("----------------LogisticRegression----------------")
fitting(grid1)
print("--------------------------------")
print(grid1.best_params_)
##########################################################################
##########################################################################
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
model_LDA = LinearDiscriminantAnalysis()
param_grid = {'store_covariance': [True],
              'n_components': [1],
              'shrinkage': [None],
              'solver': ["lsqr"]}
grid2 = GridSearchCV(model_LDA, param_grid)
print("----------------LinearDiscriminantAnalysis----------------")
fitting(grid2)
print("--------------------------------")
print(grid2.best_params_)
##########################################################################
##########################################################################
from sklearn.ensemble import RandomForestClassifier
model_RFC = RandomForestClassifier(max_depth=2, random_state=0)
param_grid = {'n_estimators': [200],
              'criterion': ["gini"],
              'max_features': ["auto"],
              'verbose': [0]
              }
grid3 = GridSearchCV(model_RFC, param_grid)
print("----------------RandomForestClassifier----------------")
fitting(grid3)
print("--------------------------------")
print(grid3.best_params_)
##########################################################################
##########################################################################
from sklearn.ensemble import GradientBoostingClassifier
model_XGB = GradientBoostingClassifier(n_estimators=100, learning_rate=1,
     max_depth=1, random_state=0)
param_grid = {'n_estimators': [120],
              'loss': ["deviance"],
              'learning_rate': [0.15],
              'verbose': [0]
              }
grid4 = GridSearchCV(model_XGB, param_grid)
print("----------------GradientBoostingClassifier----------------")
fitting(grid4)
print("--------------------------------")
print(grid4.best_params_)
##########################################################################
##########################################################################
from sklearn.naive_bayes import MultinomialNB
model_GNB = MultinomialNB()
param_grid = {'alpha': [1.0]
              }
grid5 = GridSearchCV(model_GNB, param_grid)
print("----------------MultinomialNB----------------")
fitting(grid5)
print("--------------------------------")
print(grid5.best_params_)
##########################################################################
##########################################################################
from sklearn.tree import DecisionTreeClassifier
model_DTC = DecisionTreeClassifier(random_state=0)
param_grid = {'criterion': ['gini'],
              'splitter': ['random'],
              'max_depth': [10],
              'min_samples_split': [2]
              }
grid6 = GridSearchCV(model_DTC, param_grid)
print("----------------DecisionTreeClassifier----------------")
fitting(grid6)
print("--------------------------------")
print(grid6.best_params_)
##########################################################################
##########################################################################
from sklearn.neighbors import KNeighborsClassifier
model_KNN = KNeighborsClassifier()
param_grid = {'n_neighbors': [4],
              'weights': ['uniform'],
              'algorithm': ['ball_tree']
              }
grid7 = GridSearchCV(model_KNN, param_grid)
print("----------------KNeighborsClassifier----------------")
fitting(grid7)
print("--------------------------------")
print(grid7.best_params_)
##########################################################################
##########################################################################
from sklearn.ensemble import VotingClassifier
model_voting = VotingClassifier(estimators=[
        ('LR', grid1), ('LDA', grid2), ('XGB', grid4)], voting='hard')
print("----------------VotingClassifier----------------")
fitting(model_voting)
print("--------------------------------")
##########################################################################
##########################################################################
filename = 'SVM.sav'
pickle.dump(grid, open(filename, 'wb'))
filename = 'LR.sav'
pickle.dump(grid1, open(filename, 'wb'))
filename = 'LDA.sav'
pickle.dump(grid2, open(filename, 'wb'))
filename = 'RFC.sav'
pickle.dump(grid3, open(filename, 'wb'))
filename = 'XGB.sav'
pickle.dump(grid4, open(filename, 'wb'))
filename = 'MNB.sav'
pickle.dump(grid5, open(filename, 'wb'))
filename = 'DTC.sav'
pickle.dump(grid6, open(filename, 'wb'))
filename = 'KNN.sav'
pickle.dump(grid7, open(filename, 'wb'))
filename = 'VC.sav'
pickle.dump(model_voting, open(filename, 'wb'))