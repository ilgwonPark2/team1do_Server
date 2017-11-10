property dir /Users/bag-ilgwon/GitHub/team1do_website_v2/website_v2/dist
property AppEUI 0240771000000194
property LTID 00000194d02544fffef0149a
property X-M2M-NM test_sub
property X-M2M-Origin 00000194d02544fffef0149a
property X-M2M-RI 00000194d02544fffef0149A_00012

property accept application/xml
property connect_body "<?xml version=\"1.0\" encoding=\"UTF-8\"?><m2m:sub xmlns:m2m=\"http://www.onem2m.org/xml/protocols\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"><enc><rss>1</rss></enc><nu>HTTP|http://211.253.9.191:80</nu><nct>2</nct></m2m:sub>"
property content_type_connect application/vnd.onem2m-res+xml;ty=23
property content_type_send application/xml
property send_body "<?xml version=\"1.0\" encoding=\"UTF-8\"?><m2m:mgc xmlns:m2m=\"http://www.onem2m.org/xml/protocols\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"><exe>true</exe><exra>280101</exra></m2m:mgc>"
property send_body_off "<?xml version=\"1.0\" encoding=\"UTF-8\"?><m2m:mgc xmlns:m2m=\"http://www.onem2m.org/xml/protocols\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"><exe>true</exe><exra>280100</exra></m2m:mgc>"
property uKey VS9zQkEyK3FVWlpwcHNYNXp4V2xYREVXbUdwY3dnQnhNL1dGV2FnT01scElReldhejJNRzJJclFSZ3I1bjN5UA==

property orientdb_cred root:team1do
property db_ip 211.253.9.191
property database BusDB



service id connect
  on start https.send thingplugpf.sktiot.com 9443 /$system.AppEUI$/v1_0/remoteCSE-$system.LTID$/container-LoRa POST $system.connect_body$ {"X-M2M-RI":"$system.X-M2M-RI$","X-M2M-Origin":"$system.X-M2M-Origin$","X-M2M-NM":"$system.X-M2M-NM$","uKey":"$system.uKey$","Content-Type":"$system.content_type_connect$"}
exit
service id send_data
  on start https.send thingplugpf.sktiot.com 9443 /$system.AppEUI$/v1_0/mgmtCmd-$system.LTID$_extDevMgmt PUT $system.send_body$ {"Accpet":"$system.accept$","X-M2M-RI":"$system.X-M2M-RI$","X-M2M-Origin":"$system.X-M2M-Origin$","uKey":"$system.uKey$","Content-Type":"$system.content_type_send$"}
exit
service id send_data_off
  on start https.send thingplugpf.sktiot.com 9443 /$system.AppEUI$/v1_0/mgmtCmd-$system.LTID$_extDevMgmt PUT $system.send_body_off$ {"Accpet":"$system.accept$","X-M2M-RI":"$system.X-M2M-RI$","X-M2M-Origin":"$system.X-M2M-Origin$","uKey":"$system.uKey$","Content-Type":"$system.content_type_send$"}
exit
service id test
  on start
    map.new
    map.put $last X-M2M-RI 00000194d02544fffef0149A_00012
    map.put $last X-M2M-Origin 00000194d02544fffef0149a
    map.put $last uKey VS9zQkEyK3FVWlpwcHNYNXp4V2xYREVXbUdwY3dnQnhNL1dGV2FnT01scElReldhejJNRzJJclFSZ3I1bjN5UA==
    map.put $last X-M2M-NM test_sub
    map.put $last content-type application/vnd.onem2m-res+xml;ty=23
    https.send thingplugpf.sktiot.com 9443 /$system.AppEUI$/v1_0/remoteCSE-$system.LTID$/container-LoRa POST $system.connect_body$ $last
  exit
exit

service id get_low_bus_data
  on start
    http.send ws.bus.go.kr 80 /api/rest/arrive/getLowArrInfoByStId GET "" {} {"serviceKey":"/lGKaos/Ylfttaf7fO9+7SwZ9UjlA8x0FUyXfnTut8I2T8pP6g/xNbcUuU591ilyIPa851EvrPZ8kQ9PvecrXQ==","stId":"101000004"}
    system.property.write low_bus_data (text.replace "$last.body" "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>" "")
  exit
exit
service id send_data_to_ws
  on start
    bus_data1 = $system.low_bus_data
    content = "{\"est_bus_1\":\"$bus_data1$\"}"
    interface.send websocket_server "$content$"
    debug bus_data1 $content
  exit
exit

service id orientdb_rest
  # $1 ~> SQL statement
  on start
    map.new
    map.put $last Authorization (text.join "Basic " (encode.64 $system.orientdb_cred))
    map.put $last Content-Type application/json
    http.send $system.db_ip 2480 /command/$system.database$/sql POST $1 $last
    system.property.write result $last.body.result
  exit
exit

service id xmlParser
 on start
    a = 1
    (while (service xmlParser_checker $a $1) (a = add $a 1))
 exit
exit
service id xmlParser_checker
 on start
    a = $1
    debug d1 $a
    text.contains (xml.xpath $system.low_bus_data */*/rtNm[$a$]) $2$
    if (text.equals $last true) (return false) (return true)
    debug last $last
 exit
exit
service id xmlParser_plainNo
 on start
  # $1 ~> PlainNo  $2 ~> index   $3 ~> bus_num
   xml.xpath $system.low_bus_data */*/plainNo$1$[$2$]
   do (text.replace $last "<?xml version=\"1.0\"?><plainNo1>" "") (text.replace $last "</plainNo1>" "")
 exit
exit

interface id webserver
  on #
    if (text.starts_with $data.path /api) (return (event $data.path))
    if (text.equals $data.path /) (return (file.read "$system.dir$/index.html"))
    file.read (text.join $system.dir $data.path)
  exit
  on /api/init
    service send_data_to_ws
  exit
  on /api/send_data
    service send_data
    return $system.station_data
  exit
  on /api/send_data_off
    service send_data_off
  exit
  on /api/get_xml_data
    return $system.station_data
  exit
  on /api/reserve_Bus
    busNum = $data.body.contents.bus_num
    pNum = $data.body.contents.p_num
    debug busNum $busNum
    debug pNum $pNum
    index = (service xmlParser $busNum)
    debug idx $index
    service xmlParser_plainNo $pNum $index $busNum
    debug plnNo $last
  exit
  type http server
  port 4444
exit

interface id websocket_server
  port 8081
  type ws server
  on connect respond (service init)
exit

timer id update_50sec
  interval 100000
  on start
    service get_low_bus_data
    service send_data_to_ws
  exit
  active
exit
