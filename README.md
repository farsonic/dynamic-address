SRX Firewall - Dynamic creation of address books
================================================
The SRX firewall can be configured to monitor a central web server for a list of IP Addresses to create a dynamic address book. When the SRX is referencing this service a new address 
book is created for each "feed" that is provided by the server. Each feed is turned into an address-book of the same name that is referenced directly within security policy, in much
the same way static address booked are utilized today. 

The important destination here is that by utilizing a dynamic feed there is no requirement to "commit" any changes to the configuration, the SRX simply applies policy based on the 
dynamic nature of the feed it is installing. 

Installation
============







```
* MAC Address of the user 
* Assigned IP address
* Client Identifier (if know, otherwise *)
* Requested hostname for resolution 
```
