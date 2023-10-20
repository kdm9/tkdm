# tkdm

`kdm9`'s toolkit of miscellaneous goodies. MPL2 license.


# `tkdm autogallery`

Automatically generate an HTML lightbox + gallery from a directory of images.

```
$ tree images
images/
    a/
        img1.jpg
        img2.jpg
    b/
        img3.jpg
        img4.jpg
$ tkdm autogallery -i ./images -o ./webgallery/ -t 8
```

# `tkdm genautoindex`

Automatically generate an index.html like Apache's autoindex, or caddy's `file_server browse`, only for static sites.

```
$ tkdm genautoindex
```

