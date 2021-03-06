# Hardware-Mobilizing-via-EEG-Headset
Senior Design Project

The aim of this project is hardware mobilizing with OpenBCI's EEG Headset. Two different ways were followed to achieve this. The first is Mental/Motor Imagery. In order to do this, the user who collects the data at that moment needs to imagine the movements that appear on the screen. These movements appear on the screen as gifs and the user has to imagine those movements at that moment.

The second way is performing gestures. It's about collecting more EMG data than EEG. In the same way, gifs appear on the screen and the user has to repeat the movements made there. Thus, data collection is ensured.

The collected data then goes to the pre-processing part and goes through certain processes there. For example, Outlier Detection & Elimination and Oversampling are performed for both methods. After that, the models are started to be trained. With these models, predictions are made instantly.

If you want to do all of these at once, you need to run the .py codes named pipeline in the required file. On average, it is possible to switch to the prediction part in 10 minutes. You can check the details of the headset we use in the project report. Changes to the code may be required in case of device incompatibilities or differences.


![Alt text](http://www.alpmed.com.tr/wp-content/uploads/2020/09/UCM4-Product-2_1024x1024-e1601370441949.jpg?raw=true "Title")
