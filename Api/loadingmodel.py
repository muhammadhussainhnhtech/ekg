from keras.models import load_model



model1 = load_model('hyp.h5')
model2 = load_model('sttc-training_kfold_10folds.h5')
model3 = load_model('disserithemia_v1.h5')
model4 = load_model('cd_v1.h5')
model5 = load_model('mi.h5')


