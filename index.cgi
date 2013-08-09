#!/bin/bash

## Secure Dead Drop Messaging System ##
# By Jeremy Ruhland https://github.com/JeremyRuhland/secure-dead-drop
#
# Edit variables to match your system configuration.
# Follow instructions in README to set up your system.
# Set up your webserver for CGI scripting and only allow SSL access.

# Path to webserver-user's .gnupg folder
homedir_path=/var/spool/www/.gnupg
 
# URL to remote copy of public key, to encourage users to verify.
link_to_remote_backup_pubkey="http://example.url/to/remote/pgp_pubkey"

# Recipient email, where encrypted messages will be sent to.
message_recipient="someone@example.com"

# Host email, where messages will be sent from.
message_sender="webmaster@server.org"

###############################################################################

echo $'Content-type: text/html\n'

echo '<!DOCTYPE html>
      <html>
      <head>
      <title>Secure Dead Drop</title>
      </head>
      <body>
      <form action="index.cgi" method="post">
      <table cellpadding="3" cellspacing="3" style="font-family: sans-serif;">
          <tbody>
          <tr>
              <td colspan="2"><div style="width: 350px; word-wrap: break-word"><b>Secure Dead Drop Messaging System</b><br><br>Write a message below and it will be encrypted and transmitted to me.<br><br>It is recommended that your message be signed with your key to prevent alteration.<br><br>It is also recommended that you encrypt this message to <a href="'

echo "${link_to_remote_backup_pubkey}"

echo '" target="_blank">my pubkey</a> (also available on the right) unless you are confident that this SSL connection has not been MiTMed.<br><br>Do not accept my pubkey on blind faith, verify with offline backups and public keyservs to minimize the chance of successful MiTM. Trust the <a href="https://en.wikipedia.org/wiki/User:Dotdotike/Trust_Upon_First_Use" target="_blank">TOFU.</div></td>
              <td rowspan="9" valign="bottom"><textarea name="message" style="resize: none; overflow-y: scroll; width: 480px; height: 750px; font-size:12px">'

gpg --homedir $homedir_path --export -a "$message_recipient"

echo '</textarea></td>
          </tr>
          <tr>
              <td colspan="2"><br></td>
          </tr>
          <tr>
              <td colspan="2">(Optional & Non-secure)</td>
          </tr>
          <tr>
              <td><b>Enter Name:</b></td>
              <td><textarea name="name" cols="25" rows="1" style="resize: none;"></textarea></input></td>
          </tr>
          <tr>
              <td><b>Enter Subject:</b></td>
              <td><textarea name="subject" cols="25" rows="1" style="resize: none;"></textarea></td>
          </tr>
          <tr>
              <td colspan="2"><br></td>
          </tr>
          <tr>
              <td colspan="2">(Secure)</td>
          </tr>
          <tr>
              <td colspan="2"><b>Enter Message:</b></td>
          </tr>
          <tr>
              <td colspan="2"><textarea name="message" cols="45" rows="10" style="resize: none; overflow-y: scroll;"></textarea></td>
          </tr>
          <tr>
              <td colspan="2"><input type="submit" value="Submit" /> <input type="reset" value="Clear" /></td>
              <td><a href="https://github.com/JeremyRuhland/secure-dead-drop">Secure Dead Drop</a> Coded by <a href="http://goopypanther.org">Jeremy Ruhland</a></td>
          </tr>
          </tbody>
      </table>
      </form>
      </body>
      </html>'

# This code for getting code from post data is from http://oinkzwurgl.org/bash_cgi and
# was written by Phillippe Kehi <phkehi@gmx.net> and flipflip industries.

# (internal) routine to store POST data
function cgi_get_POST_vars()
{
    # check content type
    # FIXME: not sure if we could handle uploads with this..
    [ "${CONTENT_TYPE}" != "application/x-www-form-urlencoded" ] && \
    echo "bash.cgi warning: you should probably use MIME type "\
         "application/x-www-form-urlencoded!" 1>&2
    # save POST variables (only first time this is called)
    [ -z "$QUERY_STRING_POST" \
      -a "$REQUEST_METHOD" = "POST" -a ! -z "$CONTENT_LENGTH" ] && \
        read -n $CONTENT_LENGTH QUERY_STRING_POST
    # prevent shell execution
    local t
    t=${QUERY_STRING_POST//%60//} # %60 = `
    t=${t//\`//}
    t=${t//\$(//}
    QUERY_STRING_POST=${t}
    return
}

# (internal) routine to decode urlencoded strings
function cgi_decodevar()
{
    [ $# -ne 1 ] && return
    local v t h
    # replace all + with whitespace and append %%
    t="${1//+/ }%%"
    while [ ${#t} -gt 0 -a "${t}" != "%" ]; do
    v="${v}${t%%\%*}" # digest up to the first %
    t="${t#*%}"       # remove digested part
    # decode if there is anything to decode and if not at end of string
    if [ ${#t} -gt 0 -a "${t}" != "%" ]; then
        h=${t:0:2} # save first two chars
        t="${t:2}" # remove these
        v="${v}"`echo -e \\\\x${h}` # convert hex to special char
    fi
    done
    # return decoded string
    echo "${v}"
    return
}

# routine to get variables from http requests
# usage: cgi_getvars method varname1 [.. varnameN]
# method is either GET or POST or BOTH
# the magic varible name ALL gets everything
function cgi_getvars()
{
    [ $# -lt 2 ] && return
    local q p k v s
    # prevent shell execution
    t=${QUERY_STRING//%60//} # %60 = `
    t=${t//\`//}
    t=${t//\$(//}
    QUERY_STRING=${t}
    # get query
    case $1 in
    GET)
        [ ! -z "${QUERY_STRING}" ] && q="${QUERY_STRING}&"
        ;;
    POST)
        cgi_get_POST_vars
        [ ! -z "${QUERY_STRING_POST}" ] && q="${QUERY_STRING_POST}&"
        ;;
    BOTH)
        [ ! -z "${QUERY_STRING}" ] && q="${QUERY_STRING}&"
        cgi_get_POST_vars
        [ ! -z "${QUERY_STRING_POST}" ] && q="${q}${QUERY_STRING_POST}&"
        ;;
    esac
    shift
    s=" $* "
    # parse the query data
    while [ ! -z "$q" ]; do
    p="${q%%&*}"  # get first part of query string
    k="${p%%=*}"  # get the key (variable name) from it
    v="${p#*=}"   # get the value from it
    q="${q#$p&*}" # strip first part from query string
    # decode and evaluate var if requested
    [ "$1" = "ALL" -o "${s/ $k /}" != "$s" ] && \
        eval "$k=\"`cgi_decodevar \"$v\"`\""
    done
    return
}

# register all GET and POST variables
cgi_getvars BOTH ALL

# make sure message was entered
if [ -n "$message" ]; then
 # Autofill name/subject if blank
 if [ -z "$name" ]; then
  name="No Name"
 fi
 if [ -z "$subject" ]; then
  subject="No Subject"
 fi
 # correct EOL's, encrypt and sign message
 message=`echo "$message" | tr '\r' '\n' | gpg --recipient $message_recipient -aesq`
 # assemble email data
 message="To: $message_recipient\nFrom: $message_sender\nSubject: [DeadDrop] $name: $subject\nMessage from: $name\nWith Subject: $subject\n\n$message"
 # send email data
 echo -e "$message" | /usr/sbin/sendmail -t

fi

exit 0
