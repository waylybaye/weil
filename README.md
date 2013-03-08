# Weil

Weil is an email web service platform


## USAGE

### Server side

1. Start weil web service

2. Create a mailbox which containing your smtp or AWS SES credentials


### The Client

1. Generate a token and use the token to call weil api

    POST /api/send, {
        'to': ['Tome <tom@example.com>'],
        'subject': "Please verify your email address",
        'content': "click the link below to verify your address",
        'html_content': "<html> .... </html>",
        'sender': "sender@your-host.com",
        'token': 's23d23'wer-wek2345-sdfg234',
    }

2. Finish !
