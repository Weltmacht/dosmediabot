# dosmediabot

Purpose of this application is to create a Windows Forms application for managing a queue of links from twitch chat, through donations/bits or channel points.  

## .env examples:
### Twitch OIDC request cred
```
TWITCH_APP_ID=clientID
TWITCH_APP_SECRET=clientSecret
```

### Donate amounts to queue
```
VIDEO_BIT_AMOUNT=75
VIDEO_POINT_AMOUNT=2500
```

### History to maintain between streams
```
KEEP_HISTORY_HRS=48
```

### Who to allow to request without donates
```
ALLOW_MODS=true
ALLOW_FREE=true
```

### Command Prefix for queue trigger
```
CMD_PREFIX=!vr
```

### Double click on item to copy to clipboard and delete off queue
```
DBLCLK_DEL=true
```