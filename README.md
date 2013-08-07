* auto-gen TOC:
{:toc}

# Introduction

We already know that all internet and phone traffic is being monitored. You cannot trust your email providers for private and anonymous access. Javascript is dangerous. Tor is broken in some circumstances. The PGP web-of-trust leaks user information in a dangerous way. Lets fix some of that with software designed to let users of safe computers communicate over unsafe networks.

This webapp allows anonymous users to send messages to your inbox, which arrive signed and encrypted using PGP to ensure message integrity and privacy. Only SSL connections are permitted, which ensures encrypted communication between client and server. What SSL doesn't do is give you any idea of who the server is, be it legitimate or an attacker posing as the server. The internet tires to do this identity verification using CA certs but its a mess and full of vulnerabilities. Ultimately its no better than self-signing.

The method we must use is called TOFU (Trust On First Use), you may be familiar with this if you use SSH. The client accepts the self-signed certificate and warns you if it unexpectedly changes. There are some firefox extensions such as [Certificate Patrol](https://addons.mozilla.org/en-us/firefox/addon/certificate-patrol/) that make this process easier for the end user. The only way to verify the identity of the server is by comparing the key fingerprint on a trusted channel of communication, such as in person or using a shared secret key. For numerous reasons this is beyond the scope of this project.

When a message is typed into the secure text box and submitted, it is securely transmitted to the server, encrypted using the recipient's public key, signed using the server's private key and delivered to a preprogrammed email account. More security conscious users may opt to have this email account be local to the server itself, but it can be delivered to any email account provided the server is capable of sending it.

You can see my example working installation here: https://deaddrop.goopypanther.org/index.cgi

# Inspiration

Based off [deaddrop](https://github.com/tspilk/deaddrop) by tspilk, which I found via [hackaday's article](http://hackaday.com/2013/08/03/dead-drop-concept-inspired-by-ender-wiggin-family/).

# Installation

These instructions assume that you have basic knowlage of unix and have a server capable of sending email and hosting webpages.

### Prerequisits:
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
```
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
```
Things should now be working.

