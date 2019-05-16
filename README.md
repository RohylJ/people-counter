## People Counter v2 Demo Setup
### Parts
This Demo uses a Rasberry Pi, wide angle camera module with some 3d printed parts.

The rasberry Pi can be bought [here](https://au.element14.com/raspberry-pi/raspberry-modb-512m/raspberry-pi-model-b-board/dp/2456986?gclid=EAIaIQobChMI8eKUwfWj4QIVR46PCh1G2QPXEAkYASABEgL_IfD_BwE&gross_price=true&mckv=sRDPcsyXh_dc|pcrid|59148083448|pkw||pmt||slid||product|2456986|pgrid|12550800888|ptaid|pla-403748548475|&CMP=KNC-GOO-SHOPPING-2456986)

The camera can be bought [here](https://www.littlebird.com.au/raspberry-pi-wide-angle-camera-module)

The case can be printed using the files in "case files"

To put it all together put the Rpi in the case then connect the camera with the help of a long thin object to push the lock in place. The connection can be dificult to get correct but will stay sturdy once locked in.

## SAP Leonardo
Follow instructions in this [tutorial](https://developers.sap.com/tutorials/cp-mlf-create-instance.html) up to and including step 6 to get the 

Save the ClientID & ClientSecret
Edit config.py with your ClientID, ClientSecret and enter your I number in AUTH_URL 

## Cloudinary
Create a [cloudinary](https://cloudinary.com) account to store images. Go to the console then update config.py with the cloudname, api key and api secret.

Please note the images stored on Cloudinary are currently public accessable to anyone.

## Software
Connect your rasberry Pi to the internet following this [tutorial](https://raspberrypihq.com/how-to-connect-your-raspberry-pi-to-wifi/)

Run the following to get the code on your rasberry Pi
```bash
sudo su
cd /opt
apt-get install git
git clone https://github.wdf.sap.corp/I342505/People_Counter_v2.git
```
Now test you have a working version of python3 and pip

```bash
python3
pip
```
Now if both worked with no errors move on to installing requirenments

```bash
pip install requirenments.txt
```

Now install opencv using the this [tutorial](https://tutorials-raspberrypi.com/installing-opencv-on-the-raspberry-pi/)

Test that everything works by using

```bash
python3 P_counter.py
```
If it runs and sends images to Cloudinary and outputs success messages from SAP Leonardo then we now set the python script to run on boot.

```bash
nano /etc/rc.local
```

Now scroll down and just before the 
```bash
exit 0
```
add the line
```bash
python3 /opt/P_counter.py
```


## Dashboard
1.	RapidIOT. Clone [mine](https://dshopbnehcpchampionship1.ap1.hana.ondemand.com/rapidiot/ui/dashboard/edit.html?load=../../api/dashboard/editdata/BenCounter)
2.	Change data source to go to your location

API send device key that only uses my device.


## Possible Issues
If you run into any of these issues contact me (benjamin.gonzalez@sap.com)
- camera not connected
- wifi not connected
- api's not working
