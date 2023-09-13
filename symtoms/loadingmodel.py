from keras.models import load_model
import tensorflow as tf


# model = load_model('models/version_6_ekg.h5')

model = tf.lite.Interpreter(model_path="models/model.tflite")
model.allocate_tensors()