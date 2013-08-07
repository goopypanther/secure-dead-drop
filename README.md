Inspired by https://github.com/tspilk/deaddrop
This webapp allows anonymous users to send messages to your inbox, which arrive signed and encrypted using PGP to ensure message integrity and privacy.
You can see my example working installation here: https://deaddrop.goopypanther.org/index.cgi

Installation

These instructions assume that you have basic knowlage of unix and have a server capable of sending email and hosting webpages.

Prerequisits:
 * sed
 * gnupg
 * apache or other webserver
 * sendmail or other MTA (I use ssmtpd)

First off, create the .gnupg directory for your system's webserver user (eg. www-data):
 sudo mkdir -p /var/spool/www/.gnupg
 sudo chown -R www-data:www-data /var/spool/www
 sudo chmod -R 700 /var/spool/www/.gnupg
 sudo su www-data
 
Set up a keypair; use default answers and a blank key password:
 gpg --homedir /var/spool/www/.gnupg --gen-key

Import your public key into the webserver keyring:
 gpg --homedir /var/spool/www/.gnupg --keyserver pgp.mit.edu --recv-keys person@example.com

Export the server's public key so you can import it into your client for verification of received messages:
 gpg --homedir /var/spool/www/.gnupg -a --export

Log out of the www-data shell.
 exit

Edit index.cgi variables to match your system (I assume you already have sendmail or equivalent set up, getting that working is outside the scope of this guide).

Make index.cgi executable:
 sudo chmod +x /path/to/web/root/index.cgi

Set up webserver (I assume you already have SSL set up, this is outside the scope of this guide).
Example apache configuration:
 <VirtualHost *:80>
 ServerName deaddrop.example.com
 Redirect / https://deaddrop.example.com
 </VirtualHost>

 <VirtualHost *:443>
 DocumentRoot /path/to/web/root/
 ServerName deaddrop.example.com

 SSLEngine on
 SSLCertificateFile /etc/apache2/ssl_wildcard_cert/server.crt
 SSLCertificateKeyFile /etc/apache2/ssl_wildcard_cert/server.key

 Options +ExecCGI
 AddHandler cgi-script .cgi

 </VirtualHost>

Things should now be working.
