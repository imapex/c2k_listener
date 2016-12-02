#! /usr/bin/env bash

echo Please provide the following details on your lab environment.
echo
echo "What is the address of your Mantl Control Server?  "
echo "eg: control.mantl.internet.com"
read control_address
echo
echo "What is the username for your Mantl account?  "
read mantl_user
echo
echo "What is the password for your Mantl account?  "
read -s mantl_password
echo
echo "What is the your Docker Username?  "
read docker_username
echo
echo "What is the URL to the Spark Message Broker Service?  "
read c2k_msgbroker
echo
echo "What is the Spark app key you will use for this demo?  "
read c2k_msgbroker_app_key


#export MANTL_CONTROL="$control_address"
#export MANTL_USER="$mantl_user"
#export MANTL_PASSWORD="$mantl_password"

#echo "Marathon API calls will be sent to: "
#echo "https://$MANTL_CONTROL:8080/"

cp sample-demoapp.json $docker_username-c2k_listener.json
sed -i "" -e "s/DOCKERUSER/$docker_username/g" $docker_username-c2k_listener.json
sed -i "" -e "s/MSGBROKER/$c2k_msgbroker/g" $docker_username-c2k_listener.json
sed -i "" -e "s/APPKEY/$c2k_msgbroker_app_key/g" $docker_username-c2k_listener.json


echo " "
echo "***************************************************"
echo "Installing the demoapp as  imapex/c2k/c2klistener"
curl -k -X POST -u $mantl_user:$mantl_password https://$control_address:8080/v2/apps \
-H "Content-type: application/json" \
-d @$docker_username-c2k_listener.json \
| python -m json.tool

echo "***************************************************"
echo

echo Installed

echo "Wait 2-3 minutes for the service to deploy. "
echo
echo "You can also watch the progress from the GUI at: "
echo
echo "https://$control_address/marathon"
echo
