echo "Authenticating admin..."
export OS_USERNAME=admin
export OS_TENANT_NAME=admin
export OS_PASSWORD=6abfe2ddfbfe1a71b738
export OS_AUTH_URL=http://10.5.128.227:5000/v2.0
echo "Getting image list..."
IMAGE_ID=`nova image-list | egrep cirros | egrep -v "kernel|ramdisk" | awk '{print $2}'`
echo "Booting image..."
if [ -z "$1" ]
then 
	echo "Retry with an argument.."
else 
	nova boot --flavor 1 --image $IMAGE_ID $1
fi
