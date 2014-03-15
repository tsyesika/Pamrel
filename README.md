Pamrel
======

Pastebin using restful endpoints. This is a basic pastebin but with a few features
that you may find useful:

- Syntax highlighting
- Theming (any pygments compatable theme)
- Delete after <x> many views
- Delete after a certain date
- Line numbering


Clients
-------

You can use curl:  
`$ cat some_file.c | curl -F 'content=<-' -X POST http://pamrel.lu`

There is also the following clients:
- [Emacs (https://github.com/cwebber/pamrel-el)](https://github.com/cwebber/pamrel-el) by Chris Webber
- [Chocolat (https://github.com/xray7224/pamrel.chocmixin)](https://github.com/xray7224/pamrel.chocmixin) by Jessica Tallon

Licence
-------

The pamrel pastebin code is under the AGPLv3:

[<img alt="AGPL v3" src="https://www.gnu.org/graphics/agplv3-155x51.png">](https://www.gnu.org/licenses/agpl-3.0.html)

Installing
----------

To install it simply grab the python-virtualenv stuff and then:  
`$ pip install -r requirements.txt`
