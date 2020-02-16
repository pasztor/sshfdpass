# sshfdpass

This python tool aims in helping a robust and portable
configuration tool for your ssh, using openssh's proxypassfd feature.
Originally, I have read this article, which inspired me to write this tool:
https://www.gabriel.urdhr.fr/2016/08/07/openssh-proxyusefdpass/

By portable I mean two main goal:
- Wherever is my laptop is connected, when I try to ssh to any of the hosts I want to log into, I could use the same hostname, with the same configfile
- Whatever host is I am on, I could deploy the same config to everywhere (eg. with some ansible recipe) and like with my laptop's case: host foo means always host foo, and the way to get there should be based on sshfdpass configured rules.

The base of this main concept is, that for most of your host definitions in your ssh configuration, you only need to define the ssh-specific settings; like in this example:

```
Host foo
ForwardAgent yes
```

But, at the end of your `.ssh/config` this _fallback_ setting should be
provided:

```
Host *
ProxyUseFDPass yes
ProxyCommand sshfdpass "%h" "%p"
```

While you can simply define tests and final actions to do.

In this simple example, let's assume you have an ssh server in your home dmz, available directly from your home lan via the **1.2.3.4** ip address on the port **122**, while from the outside world you can access the same server via the **4.3.2.1** ip address on the default port, and your home network can be recognized by the fact that your (source) IP address is **192.168.0.x**.

```
tests:
  homenet:
    ipv4range:
      - 192.168.0.0/24
  someothernet:
    ipv4range:
      - 10.2.4.0/24

 rules:
   foo:
     - test: homenet
       action: tcp4
       tcp4.host: 1.2.3.4
     - test:
         ipv4range:
           - 10.1.2.0/24
       action: tcp4
       tcp4.host: 10.1.2.1
     - action: tcp4
       tcp4.host: 4.3.2.1 
```
