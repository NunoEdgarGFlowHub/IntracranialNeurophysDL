import matplotlib.pyplot as plt
import numpy as np
from data.utils.fileio import load_joeyo_reaching
from data.utils.KalmanFilter import ManualKalmanFilter as mkf
from pathlib import Path

# Sampling rate of behaviour and spike rate data (we assume equal)
BEHAV_RATE = 250.
SPIKES_RATE = 244.140625
# Loading the data-set
datadir = Path.cwd()
sess_names = ['indy_2016' + _ for _ in ['0921_01', '0927_04', '0927_06', '0930_02', '0930_05' '1005_06' '1006_02']]
# We use the first session here
sess_name = sess_names[0]
# Extracting spike rates and cursor positions
spike_rate, behav, spike_rate_ax_info, behav_ax_info = load_joeyo_reaching(datadir, sess_name, x_chunk='spikerates')
cursor_pos = behav[:2, :]
# Choosing our state to be the cursor position
x = cursor_pos
# Adding cursor velocity to our state vector
x_d = np.zeros_like(x)
x_d[:, 1:] = np.diff(x, axis=1) * BEHAV_RATE
x = np.vstack((x, x_d))
# Choosing half of the data set for training (In practice it could be any portion higher than 50%)
training_size = int(0.5 * np.size(x, 1))
# Dividing our state and neural (spike rates) data to training and test
x_training = x[:, :training_size]
z_training = spike_rate[:, :training_size]
x_test = x[:, training_size:]
z_test = spike_rate[:, training_size:]
# The empty array to store in our predicted states later
x_predict = np.zeros_like(x_test)
# Instantiating a Kalman filter object (Inputs are state and neural training data
mykf = mkf(x=x_training, z=z_training)
# just because it's slow to do the whole test data
rng = int(0.03*np.size(x_test, 1))
# Estimating a state with each of neural test data
for i in range(rng):
    mykf.predict()
    z_in = z_test[:, i]
    x_predict[:, i] = np.reshape(mykf.update(z_in), (mykf.m, ))
    if i%50 == 0:
        print('Step: ' + str(i) + ' out of ' + str(rng))
# Plotting the estimated states against the actual cursor positions
plt.figure(1)
plt.subplot(2,1,1)
plt.plot(x_predict[0, :rng], label="x-predicted")
plt.plot(x_test[0, :rng], label="x-actual")
plt.legend()
plt.subplot(2,1,2)
plt.plot(x_predict[1, :rng], label="y-predicted")
plt.plot(x_test[1, :rng], label="y-actual")
plt.legend()
plt.figure(2)
plt.plot(x_predict[0, :rng], x_predict[1, :rng], label="predicted")
plt.plot(x_test[0, :rng], x_test[1, :rng], label="actual")
plt.legend()
plt.show()
