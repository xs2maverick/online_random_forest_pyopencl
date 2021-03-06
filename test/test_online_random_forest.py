import online_random_forest as orf
import libsvm_format as libsvm
import unittest
from sklearn.mixture import GMM
import numpy
import curses
from time import time

class TestOnlineRandomForest(unittest.TestCase):
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_create_DecisionTree(self):
    dt=orf.DecisionTree(10)

  def test_GMM(Self):
    X=[0.9,1.,1.9,2.,2.1,1.1]
    gmm=GMM(n_components=2, covariance_type='spherical', init_params='wc', n_iter=20)
    gmm.fit(X)
    y_train_predict=gmm.predict(X)
    assert list(y_train_predict)==[1,1,0,0,0,1] or list(y_train_predict)==[0,0,1,1,1,0]
    assert gmm.means_.mean()>1.45 and gmm.means_.mean()<1.55

  def test_predict_without_samples(self):
    d=orf.DecisionTree(
      1, number_of_decision_functions=1, 
      min_samples_to_split=2,
      predict_without_samples={
        'mean':5.0,
        'variance':1.0,
        'num_samples':7})
    assert d.predict([1.])==5.
    d.update([1.], 10.)
    assert d.predict([1.])==7.5
    d.update([1.], 10.)
    assert d.predict([1.])==10.
  
  def test_libsvm_reading(self):
    (y,x)=libsvm.svm_read_problem('data/libsvm/dna.scale.tr')
    assert x[0][5]==1.
    print x[0]
    assert y[0]==2.
    print x[3]
    print y[3]

    print "y"
    print y[0], y[1], y[2], y[3], y[4], y[5], y[6], y[7]


  def row_as_numpy_array(self, row):
    npa=numpy.zeros(181)
    for key, value in row.iteritems():
      npa[key]=value
    return npa
  
  def predict_libsvm_set_classification(sefl, rf, x, y):
    total=len(x)
    correct=0
    predictions=[]
    for i, row in enumerate(x):
      row_as_np_array=numpy.zeros(181)
      for key, value in row.iteritems():
        row_as_np_array[key]=value
      prediction, variance=rf.predict(row_as_np_array)
      predictions.append(prediction)
      prediction=prediction[0]
      if prediction==y[i]:
        correct+=1
    print numpy.array(predictions)
    print correct/float(total)

  def predict_libsvm_set_regression(sefl, rf, x, y):
    total=len(x)
    correct=0
    predictions=[]
    for i, row in enumerate(x):
      row_as_np_array=numpy.zeros(181)
      for key, value in row.iteritems():
        row_as_np_array[key]=value
      prediction, variance=rf.predict(row_as_np_array)
      predictions.append(prediction)
      prediction=int(round(prediction))
      if prediction==y[i]:
        correct+=1
    print numpy.array(predictions)
    print correct/float(total)


  def _test_online_random_forest_classifier(self):
    rf=orf.OnlineRandomForestClassifierOpenCLSplit(
      number_of_features=181,
      number_of_samples_to_split=10,
      number_of_decision_functions_at_node=180,
      number_of_trees=100
      )
    (y,x)=libsvm.svm_read_problem('data/libsvm/dna.scale.tr')
    t=time()
    for k in range(1):
      for i,row in enumerate(x):
          #if i<10:
          row_as_np_array=self.row_as_numpy_array(row)
          row_as_np_array=numpy.zeros(181)
          for key,value in row.iteritems():
            row_as_np_array[key]=value
          print "                                                                         Update", k, i
          rf.update(row_as_np_array, y[i])
    opencltime=time()-t

    print "Predicting training ..."
    self.predict_libsvm_set_classification(rf, x, y)
    print "Predicting test ..."
    (y,x)=libsvm.svm_read_problem('data/libsvm/dna.scale.t')
    self.predict_libsvm_set_classification(rf, x, y)

    rf=orf.OnlineRandomForestClassifier(
      number_of_features=181,
      number_of_samples_to_split=10,
      number_of_decision_functions_at_node=180,
      number_of_trees=100
      )
    (y,x)=libsvm.svm_read_problem('data/libsvm/dna.scale.tr')
    t=time()
    for k in range(1):
      for i,row in enumerate(x):
          #if i<10:
          row_as_np_array=self.row_as_numpy_array(row)
          row_as_np_array=numpy.zeros(181)
          for key,value in row.iteritems():
            row_as_np_array[key]=value
          print "                                                                         Update", k, i
          rf.update(row_as_np_array, y[i])
    noopencltime=time()-t

    print "Predicting training ..."
    self.predict_libsvm_set_classification(rf, x, y)
    print "Predicting test ..."
    (y,x)=libsvm.svm_read_problem('data/libsvm/dna.scale.t')
    self.predict_libsvm_set_classification(rf, x, y)
    print "OpenCL Classification Speedup is:" ,noopencltime/opencltime

    
  def test_online_random_forest_regressor(self):
    rf=orf.OnlineRandomForestRegressorSecretOpenCL(
      number_of_features=181,
      number_of_samples_to_split=10,
      number_of_decision_functions_at_node=180,
      number_of_trees=20
      )
    (y,x)=libsvm.svm_read_problem('data/libsvm/dna.scale.tr')
    
    t=time()
    for k in range(1):
      for i,row in enumerate(x):
          #if i<10:
          row_as_np_array=self.row_as_numpy_array(row)
          row_as_np_array=numpy.zeros(181)
          for key,value in row.iteritems():
            row_as_np_array[key]=value
          print "                                                                         Update", k, i
          rf.update(row_as_np_array, y[i])
    opencltime=time()-t

    print "Predicting training opencl ..."
    self.predict_libsvm_set_regression(rf, x, y)
    print "Predicting test opencl ..."
    (y,x)=libsvm.svm_read_problem('data/libsvm/dna.scale.t')
    self.predict_libsvm_set_regression(rf, x, y)

    rf=orf.OnlineRandomForestRegressor(
      number_of_features=181,
      number_of_samples_to_split=10,
      number_of_decision_functions_at_node=180,
      number_of_trees=20
      )
    (y,x)=libsvm.svm_read_problem('data/libsvm/dna.scale.tr')
    
    t=time()
    for k in range(1):
      for i,row in enumerate(x):
          #if i<10:
          row_as_np_array=self.row_as_numpy_array(row)
          row_as_np_array=numpy.zeros(181)
          for key,value in row.iteritems():
            row_as_np_array[key]=value
          print "                                                                         Update", k, i
          rf.update(row_as_np_array, y[i])
    noopencltime=time()-t

    print "Predicting training no opencl..."
    self.predict_libsvm_set_regression(rf, x, y)
    print "Predicting test no opencl ..."
    (y,x)=libsvm.svm_read_problem('data/libsvm/dna.scale.t')
    self.predict_libsvm_set_regression(rf, x, y)

    print "OpenCL Secret Regression Speedup is:", noopencltime/opencltime 



  def test_online_random_forest(self):
    x=[
      [1,2,3],
      [2,3,5],
      [1,3,8],
      [2,8,3]
      ]
    y=[1,2,1,2]
    rf=orf.OnlineRandomForestRegressor(
      number_of_features=3,
      number_of_samples_to_split=2,
      number_of_decision_functions_at_node=3
      )
    for k in range(2):
      for i,row in enumerate(x):
        row_as_np_array=numpy.array(row)
        print row_as_np_array
        rf.update(row_as_np_array, y[i])

    x=[
      [1,2,4],
      [2,5,3],
      [1,7,8]
      ]
    y=[1,2,1]
    total=len(x)
    correct=0
    predictions=[]
    for i, row in enumerate(x):
      row_as_np_array=numpy.array(row)
      prediction, variance=rf.predict(row_as_np_array)
      predictions.append((prediction, variance))
      prediction=int(round(prediction))
      if prediction==y[i]:
        correct+=1
    print predictions
    print correct/float(total)








if __name__=='__main__':
  unittest.main()
