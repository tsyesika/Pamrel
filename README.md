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

There is a python client which offers a number of options:  
`$ pamrel --theme=wombat --syntax --numbers some_file.c`

You can also use curl:  
`$ cat some_file.c | curl -F 'content=<-' -X POST http://pamrel.lu`

I welcome others to write clients too.

Licence
-------

The pamrel pastebin code is under the AGPLv3:

[<img alt="AGPL v3" src="https://www.gnu.org/graphics/agplv3-155x51.png">](https://www.gnu.org/licenses/agpl-3.0.html)

Installing
----------

To install it simply grab the python-virtualenv stuff and then:  
`$ pip install -r requirements.txt`
