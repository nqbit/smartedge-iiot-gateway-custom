#!/bin/sh
sleep 10

rm /etc/machine-id
# set one time machine id
systemd-machine-id-setup

# Build device id
export SERIAL=`cat /proc/cpuinfo| grep Serial| cut -d':' -f2`


# Verify TPM is authentic, HALT if not authentic.
# read the RSA cert and verify it
tpm2_nvread --index 0x1c00002 >/tmp/ek_cert_rsa.der
openssl x509 -inform der -in /tmp/ek_cert_rsa.der -out /tmp/ek_cert_rsa.pem
openssl verify -CAfile /usr/bin/Infineon-TPM.ca /tmp/ek_cert_rsa.pem
# if verified, etxract the public key from the cert
if [ $? -eq 0 ]; then
      openssl x509 -noout -pubkey -in /tmp/ek_cert_rsa.pem >/tmp/ek_rsa_pub_from_crt.pem
    echo RSA verified OK
else
    echo RSA verification FAILED
    exit 1
fi

# read the ECC cert and verify it 
tpm2_nvread --index 0x1c0000a >/tmp/ek_cert_ecc.der
openssl x509 -inform der -in /tmp/ek_cert_ecc.der -out /tmp/ek_cert_ecc.pem
openssl verify -CAfile /usr/bin/Infineon-TPM.ca /tmp/ek_cert_ecc.pem
# if verified, etxract the public key from the cert
if [ $? -eq 0 ]; then
    openssl x509 -noout -pubkey -in /tmp/ek_cert_ecc.pem >/tmp/ek_ecc_pub_from_crt.pem
    echo ECC verified OK
else
    echo ECC verification FAILED
    exit 1
fi

#create the EK with default EK template (like infineon did) for both RSA and ECC

tpm2_createek -G rsa -p /tmp/ek_rsa_pub_from_tpm.pem -f pem

tpm2_createek -G ecc -p /tmp/ek_ecc_pub_from_tpm.pem -f pem


#check that public keys are matching 
diff /tmp/ek_rsa_pub_from_crt.pem /tmp/ek_rsa_pub_from_tpm.pem
if [ $? -eq 0 ]; then
    echo RSA keys match OK
else
    echo RSA keys match FAILED
    exit 1
fi
diff /tmp/ek_ecc_pub_from_crt.pem /tmp/ek_ecc_pub_from_tpm.pem
if [ $? -eq 0 ]; then
    echo ECC keys match OK
else
    echo ECC keys match FAILED
    exit 1
fi
# Were a genuine TPM2 Infineon chip 
echo TPM2InfineonChipGenuine
tpm2_dictionarylockout -c
tpm2_evictcontrol -c 0x81000001 -p 0x81000001
rm /tmp/*.der
#
#  The TPM is authenticated, now do some onetime setups for IMA/EVM
# primary key used for keyctl trusted keys
tpm2_createprimary --hierarchy o -G rsa  -o /tmp/key.ctxt
if [ $? -eq 0 ]; then
    echo OKCreatePrimary
else
    echo FAILCreatePrimary
fi
tpm2_evictcontrol -c /tmp/key.ctxt -p 0x81000001
if [ $? -eq 0 ]; then
    echo OKEvictControl
else
    echo FAILEvictControl
fi

# get certs from Infineon stored in TPM we will use these for the IMA and EVM keys
tpm2_nvread --index 0x1c00002 >/tmp/0x1c00002.der
if [ $? -eq 0 ]; then
    echo OK1c00002.der
else
    echo FAIL1c00002.der
    exit1
fi
tpm2_nvread --index 0x1c0000a >/tmp/0x1c0000a.der
if [ $? -eq 0 ]; then
    echo OK1c0000a.der
else
    echo FAIL1c0000a.der
    exit 1
fi
openssl x509 -in /tmp/0x1c0000a.der -inform der -text >/tmp/x509_evm.der
if [ $? -eq 0 ]; then
    echo OKEvmX509
else
    echo FAILEvmX509
    exit 1
fi
openssl x509 -in /tmp/0x1c00002.der -inform der -text >/tmp/x509_ima.der
if [ $? -eq 0 ]; then
    echo OKImaX509
else
    echo FAILImaX509
    exit 1
fi
sudo mkdir /etc/keys
sudo cp /tmp/x* /etc/keys/
# create trusted keys for ima/evm TODO!!

