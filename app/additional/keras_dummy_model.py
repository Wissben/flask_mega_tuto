import os
import tempfile
from time import time

import tensorflow as tf
from tensorflow.python import keras

ORIGINAL_INPUT_DIM = (26, 65)
ORIGINAL_FLATTEN_INPUT_DIM = ORIGINAL_INPUT_DIM[0] * ORIGINAL_INPUT_DIM[1]
FINAL_DIM = 1


def save_model(model, version=1, name=None):
    if name is None:
        name = 'model-{}'.format(time())
    MOLDE_DIR = tempfile.gettempdir()
    EXPORT_PATH = os.path.join(MOLDE_DIR, version.__str__())
    print('Exporting to {}'.format(EXPORT_PATH))
    if os.path.isdir(EXPORT_PATH):
        answer = input('Model already existing, overwrite it ?')
        if (answer.lower() is 'y'):
            print('Removing model')
            os.remove(EXPORT_PATH)
    tf.saved_model.simple_save(
        keras.backend.get_session(),
        EXPORT_PATH,
        inputs={'input_image': model.input},
        outputs={t.name: t for t in model.outputs}
    )
    print('Model saved at {}'.format(EXPORT_PATH))


def build_model(name=None):
    if name is None:
        name = 'Dummy'
    inputs = keras.Input(shape=(ORIGINAL_FLATTEN_INPUT_DIM,), name=name)
    x = keras.layers.Dense(32, activation='relu')(inputs)
    x = keras.layers.Lambda(lambda x: keras.backend.random_uniform([1, ]))(x)
    model = keras.Model(inputs=inputs, outputs=x, name='test')
    model.compile(optimizer='adam', loss='mse')
    return model


# a = np.array([v for v in range(ORIGINAL_FLATTEN_INPUT_DIM)])
# print(a.shape)
# prediction = model.predict(x=[[a]], verbose=1)
# print(prediction)
model = build_model('test')
save_model(model,1)
