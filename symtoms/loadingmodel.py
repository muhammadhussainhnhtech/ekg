# from keras.models import load_model
# import tensorflow as tf
import pickle

# #ekg models
# model = tf.lite.Interpreter(model_path="models/model_7.tflite")
# model.allocate_tensors()

# #beta testing

with open('models/beta/updated_disease_model.pkl', 'rb') as file:
    disease_model = pickle.load(file)

with open('models/beta/updated_tests_model.pkl', 'rb') as file:
    tests_model = pickle.load(file)

