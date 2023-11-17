package com.example.carplay_android.services;

import static com.example.carplay_android.javabeans.JavaBeanFilters.*;

import android.app.Notification;
import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.ServiceConnection;
import android.graphics.drawable.BitmapDrawable;
import android.os.Bundle;
import android.os.IBinder;
import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;
import android.util.Log;
import android.widget.Toast;
import android.text.Spanned;
import java.util.Set;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import com.example.carplay_android.utils.BroadcastUtils;
import com.example.carplay_android.utils.DirectionUtils;

import java.util.Arrays;
import java.util.Objects;
import java.util.Timer;
import java.util.TimerTask;


public class NotificationService extends NotificationListenerService {
    private static final String TAG = NotificationService.class.getSimpleName();
    private BleService.BleBinder controlBle;
    private ServiceConnToBle serviceConnToBle;
    private Boolean deviceStatus = false;
    private Timer timerSendNotification;
    private Boolean ifSendNotification = false;
    private static String[] informationMessageSentLastTime = new String[7];

    public NotificationService() {

    }


    @Override
    public void onCreate() {
        super.onCreate();
        init();

    }

    @Override
    public void onNotificationPosted(StatusBarNotification sbn) {
        super.onNotificationPosted(sbn);
        //Bundle extras = sbn.getNotification().extras;
        //for (String key: extras.keySet())
        //{
        //    Log.d ("myApplication", key + " is a key in the bundle");
        //}
        // Get all keys from the extras bundle
        //Set<String> allKeys = extras.keySet();

        // Iterate through the keys and do something with each key
        //for (String key : allKeys) {
            //Object value = extras.get(key);
            // Do something with the key and value
            // For example, you can log them or process them as needed
            //Log.d("NotificationKeys", "Key: " + key + ", Value: " + value);

        //}
        //Log.d("NotificationKeys", "  ");
        //Log.d("NotificationKeys", "  ");
        if (sbn != null && isGMapNotification(sbn)) {
            handleGMapNotification(sbn);
        }
    }

    @Override
    public void onNotificationRemoved(StatusBarNotification sbn) {
        super.onNotificationRemoved(sbn);
        Log.d("Notification", "removed");
    }

    public static void cleanLastTimeSent() {
        Arrays.fill(informationMessageSentLastTime, "");
    }


    private boolean isGMapNotification(StatusBarNotification sbn) {
        if (!sbn.isOngoing() || !sbn.getPackageName().contains("com.google.android.apps.maps")) {
            return false;
        }
        return (sbn.getId() == 1);
    }


    private void handleGMapNotification(StatusBarNotification sbn) {
        Bundle bundle = sbn.getNotification().extras;
        //Notification bundle = sbn.getNotification();
        //showToast("Notification: " + notification);
        String[] informationMessage = new String[7];
        String pack = sbn.getPackageName();
        String ticker = "";
        if (sbn.getNotification().tickerText != null) {
            ticker = (String) sbn.getNotification().tickerText;
        }

        // Access the notification content
        Bundle extras = sbn.getNotification().extras;
        //for (String key: extras.keySet())
        //{
        //    Log.d ("myApplication", key + " is a key in the bundle");
        //}
        // Get all keys from the extras bundle
        Set<String> allKeys = extras.keySet();

        // Iterate through the keys and do something with each key
        for (String key : allKeys) {
            Object value = extras.get(key);
            // Do something with the key and value
            // For example, you can log them or process them as needed
            Log.d("NotificationKeys", "Key: " + key + ", Value: " + value);
        }
        CharSequence titleCharSeq = extras.getCharSequence("android.title");
        String title = (titleCharSeq instanceof Spanned) ?
                ((Spanned) titleCharSeq).toString() : (titleCharSeq != null ? titleCharSeq.toString() : null);

        CharSequence textCharSeq = extras.getCharSequence("android.text");
        String text = (textCharSeq instanceof Spanned) ?
                ((Spanned) textCharSeq).toString() : (textCharSeq != null ? textCharSeq.toString() : null);
        CharSequence subtextCharSeq = extras.getCharSequence("android.subText");
        String subtext = (subtextCharSeq instanceof Spanned) ?
                ((Spanned) subtextCharSeq).toString() : (subtextCharSeq != null ? subtextCharSeq.toString() : null);
        CharSequence infotextCharSeq = extras.getCharSequence("android.infoText");
        String infotext = (infotextCharSeq instanceof Spanned) ?
                ((Spanned) infotextCharSeq).toString() : (infotextCharSeq != null ? infotextCharSeq.toString() : null);

        Log.i("Notification", "Package: " + pack + "\nTicker: " + ticker + "\nTitle: " + title + "\nText: " + text + "\nsubText: " + subtext + "\ninfoText: " + infotext);
        //String string = bundle.getString(Notification.EXTRA_TEXT);

        //Log.i("Notification", "Text: " + string);
        //showToast(bundle.getString(Notification.EXTRA_TEXT));
        if (subtext != null) {
            try {
                String string = subtext;
                String[] strings = string.split("-");//destination
                //informationMessage[0] = strings[0].trim();
                informationMessage[0] = "N/A";
                strings = strings[1].trim().split(" ");
                if (strings.length == 3) {
                    strings[0] = strings[0] + " ";//concat a " "
                    strings[0] = strings[0] + strings[1];//if use 12 hour type, then concat the time and AM/PM
                }
                //informationMessage[1] = strings[0];// get the ETA

                string = title;
                strings = string.split("-");
                if (strings.length == 2) {
                    informationMessage[2] = strings[1].trim();//Distance to next direction
                    informationMessage[3] = strings[0].trim();//Direction to somewhere
                } else if (strings.length == 1) {
                    informationMessage[2] = strings[0].trim();//Direction to somewhere
                    informationMessage[3] = "N/A";//Distance to next direction
                }

                string = subtext;
                strings = string.split("·");
                informationMessage[4] = strings[0].trim();//ETA in Minutes
                informationMessage[5] = strings[1].trim();//Distance

                BitmapDrawable bitmapDrawable = (BitmapDrawable) sbn.getNotification().getLargeIcon().loadDrawable(getApplicationContext());

                informationMessage[6] = String.valueOf(DirectionUtils.getDirectionNumber(DirectionUtils.getDirectionByComparing(bitmapDrawable.getBitmap())));
                Log.d("say gex", Arrays.toString(informationMessage));
            } catch (NullPointerException e) {
                showToast("Fuckkkkkkkk kan destination niet lezen :(");
                //showToast(string);
                //Log.d(TAG, "Something went wrong i guess", e);
                //Log.d(TAG, string, e);
            }


            if (deviceStatus) {
                if (!informationMessage[0].equals(informationMessageSentLastTime[0])) {//destination
                    controlBle.sendDestination(informationMessage[0]);
                    informationMessageSentLastTime[0] = informationMessage[0];
                }
                if (!Objects.equals(informationMessage[1], informationMessageSentLastTime[1])) {//ETA
                    controlBle.sendEta(informationMessage[1]);
                    informationMessageSentLastTime[1] = informationMessage[1];
                }
                if (!Objects.equals(informationMessage[2], informationMessageSentLastTime[2])) {//direction

                    if (informationMessage[2].length() > 20) {
                        controlBle.sendDirection(informationMessage[2].substring(0, 20) + "..");
                    } else {
                        controlBle.sendDirection(informationMessage[2]);
                    }

                    informationMessageSentLastTime[2] = informationMessage[2];
                }
                if (!Objects.equals(informationMessage[3], informationMessageSentLastTime[3])) {

                    controlBle.sendDirectionDistances(informationMessage[3]);

                    informationMessageSentLastTime[3] = informationMessage[3];
                }
                if (!Objects.equals(informationMessage[4], informationMessageSentLastTime[4])) {

                    controlBle.sendEtaInMinutes(informationMessage[4]);

                    informationMessageSentLastTime[4] = informationMessage[4];
                }
                if (!Objects.equals(informationMessage[5], informationMessageSentLastTime[5])) {

                    controlBle.sendDistance(informationMessage[5]);

                    informationMessageSentLastTime[5] = informationMessage[5];
                }
                if (!Objects.equals(informationMessage[6], informationMessageSentLastTime[6])) {

                    controlBle.sendDirectionPrecise(informationMessage[6]);

                    informationMessageSentLastTime[6] = informationMessage[6];
                }
                Log.d("d", "done");
                informationMessageSentLastTime = informationMessage;
                ifSendNotification = false;//reduce the frequency of sending messages
                //why not just check if two messages are the same,  why still need to send same message every half second:
                //because if the device lost connection before, we have to keep send message to it to keep it does not
                //receive any wrong message.
            }
        }
    }


    private void init() {
        Arrays.fill(informationMessageSentLastTime, "");

        initService();
        initBroadcastReceiver();
        setSendNotificationTimer();
        BroadcastUtils.sendStatus(true, getFILTER_NOTIFICATION_STATUS(), getApplicationContext());
        DirectionUtils.loadSamplesFromAsserts(getApplicationContext());
    }

    private void initService() {
        serviceConnToBle = new ServiceConnToBle();
        Intent intent = new Intent(this, BleService.class);
        bindService(intent, serviceConnToBle, BIND_AUTO_CREATE);
        startService(intent);//bind the service
    }

    private void initBroadcastReceiver() {
        LocalBroadcastManager localBroadcastManager = LocalBroadcastManager.getInstance(getApplicationContext());
        ReceiverForDeviceStatus receiverForDeviceStatus = new ReceiverForDeviceStatus();
        IntentFilter intentFilterForDeviceStatus = new IntentFilter(getFILTER_DEVICE_STATUS());
        localBroadcastManager.registerReceiver(receiverForDeviceStatus, intentFilterForDeviceStatus);
    }

    private class ServiceConnToBle implements ServiceConnection {
        @Override
        public void onServiceConnected(ComponentName name, IBinder iBinder) {
            controlBle = (BleService.BleBinder) iBinder;
        }

        @Override
        public void onServiceDisconnected(ComponentName name) {
        }
    }

    private class ReceiverForDeviceStatus extends BroadcastReceiver {
        @Override
        public void onReceive(Context context, Intent intent) {
            deviceStatus = intent.getBooleanExtra(getFILTER_DEVICE_STATUS(), false);
        }
    }

    public void setSendNotificationTimer() {
        if (timerSendNotification == null) {
            timerSendNotification = new Timer();
            TimerTask timerTask = new TimerTask() {
                @Override
                public void run() {
                    ifSendNotification = true;
                }
            };
            timerSendNotification.schedule(timerTask, 10, 2000);
        }
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        BroadcastUtils.sendStatus(false, getFILTER_NOTIFICATION_STATUS(), getApplicationContext());
        unbindService(serviceConnToBle);
    }
    private void showToast(String message) {
        // Display a toast message on the screen
        Toast.makeText(getApplicationContext(), message, Toast.LENGTH_SHORT).show();
    }
    public static String getStringBetweenTwoCharacters(String input, String to, String from)
    {
        return input.substring(input.indexOf(to)+1, input.lastIndexOf(from));
    }
}