dir /Users/bag-ilgwon/GitHub/team1do_website_v2/website_v2/dist
AppEUI 0240771000000194
LTID 00000194d02544fffef0149a
X-M2M-NM test_sub
X-M2M-Origin 00000194d02544fffef0149a
X-M2M-RI 00000194d02544fffef0149A_00012

accept application/xml
connect_body "<?xml version=\"1.0\" encoding=\"UTF-8\"?><m2m:sub xmlns:m2m=\"http://www.onem2m.org/xml/protocols\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"><enc><rss>1</rss></enc><nu>HTTP|http://211.253.9.191:80</nu><nct>2</nct></m2m:sub>"
content_type_connect application/vnd.onem2m-res+xml;ty=23
content_type_send application/xml
send_body "<?xml version=\"1.0\" encoding=\"UTF-8\"?><m2m:mgc xmlns:m2m=\"http://www.onem2m.org/xml/protocols\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"><exe>true</exe><exra>280101</exra></m2m:mgc>"
send_body_off "<?xml version=\"1.0\" encoding=\"UTF-8\"?><m2m:mgc xmlns:m2m=\"http://www.onem2m.org/xml/protocols\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"><exe>true</exe><exra>280100</exra></m2m:mgc>"
uKey VS9zQkEyK3FVWlpwcHNYNXp4V2xYREVXbUdwY3dnQnhNL1dGV2FnT01scElReldhejJNRzJJclFSZ3I1bjN5UA==

orientdb_cred root:team1do
db_ip 211.253.9.191
database BusDB


service connect
  on start https.send thingplugpf.sktiot.com 9443 /$workspace.AppEUI$/v1_0/remoteCSE-$workspace.LTID$/container-LoRa POST $workspace.connect_body$ {"X-M2M-RI":"$workspace.X-M2M-RI$","X-M2M-Origin":"$workspace.X-M2M-Origin$","X-M2M-NM":"$workspace.X-M2M-NM$","uKey":"$workspace.uKey$","Content-Type":"$workspace.content_type_connect$"}
exit
service send_data
  on start https.send thingplugpf.sktiot.com 9443 /$workspace.AppEUI$/v1_0/mgmtCmd-$workspace.LTID$_extDevMgmt PUT $workspace.send_body$ {"Accpet":"$workspace.accept$","X-M2M-RI":"$workspace.X-M2M-RI$","X-M2M-Origin":"$workspace.X-M2M-Origin$","uKey":"$workspace.uKey$","Content-Type":"$workspace.content_type_send$"}
exit
service send_data_off
  on start https.send thingplugpf.sktiot.com 9443 /$workspace.AppEUI$/v1_0/mgmtCmd-$workspace.LTID$_extDevMgmt PUT $workspace.send_body_off$ {"Accpet":"$workspace.accept$","X-M2M-RI":"$workspace.X-M2M-RI$","X-M2M-Origin":"$workspace.X-M2M-Origin$","uKey":"$workspace.uKey$","Content-Type":"$workspace.content_type_send$"}
exit
service test
  on start
    map.new
    map.put $last X-M2M-RI 00000194d02544fffef0149A_00012
    map.put $last X-M2M-Origin 00000194d02544fffef0149a
    map.put $last uKey VS9zQkEyK3FVWlpwcHNYNXp4V2xYREVXbUdwY3dnQnhNL1dGV2FnT01scElReldhejJNRzJJclFSZ3I1bjN5UA==
    map.put $last X-M2M-NM test_sub
    map.put $last content-type application/vnd.onem2m-res+xml;ty=23
    https.send thingplugpf.sktiot.com 9443 /$workspace.AppEUI$/v1_0/remoteCSE-$workspace.LTID$/container-LoRa POST $workspace.connect_body$ $last
  exit
exit

service get_low_bus_data
  on start
    http.send ws.bus.go.kr 80 /api/rest/arrive/getLowArrInfoByStId GET "" {} {"serviceKey":"/lGKaos/Ylfttaf7fO9+7SwZ9UjlA8x0FUyXfnTut8I2T8pP6g/xNbcUuU591ilyIPa851EvrPZ8kQ9PvecrXQ==","stId":"101000004"}
    workspace.property.write low_bus_data (text.replace "$last.body" "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>" "")
  exit
exit
service send_data_to_ws
  on start
    bus_data1 = $workspace.low_bus_data
    content = "{\"est_bus_1\":\"$bus_data1$\"}"
    interface.send websocket_server "$content$"
    debug bus_data1 $content
  exit
exit
service orientdb_rest
  on start
    map.new
    map.put $last Authorization (text.join "Basic " (encode.64 $workspace.orientdb_cred))
    map.put $last Content-Type application/json
    http.send $workspace.db_ip 2480 /command/$workspace.database$/sql POST $1 $last
    debug db_REST $last.body
  exit
exit
service xmlParser
 on start
    do (a = 1) (while (is.equal (service xmlParser_checker $a $1) true) (a = add $a 1))
 exit
exit
service xmlParser_checker
 on start
    a = $1
    text.contains (xml.xpath $workspace.low_bus_data */*/rtNm[$a$]) $2$
    if (text.equals $last true) (return false) (return true)
    debug last $last
 exit
exit
service xmlParser_tagName
  on start
    # $1 ~> PlainNo  $2 ~> index
  xml.xpath $workspace.low_bus_data */*/$1$[$2$]
  do (text.replace $last "<?xml version=\"1.0\"?><$1$>" "") (text.replace $last "</$1$>" "")
 exit
exit

interface webserver
  on #
    if (text.starts_with $data.path /api) (return (event $data.path))
    if (text.equals $data.path /) (return (file.read "$workspace.dir$/index.html"))
    file.read (text.join $workspace.dir $data.path)
  exit
  on /api/send_data
    service send_data
    return $workspace.station_data
  exit
  on /api/send_data_off
    service send_data_off
  exit
  on /api/get_xml_data
    return $workspace.station_data
  exit
  on /api/init
    service send_data_to_ws
    service orientdb_rest "select rtNm, isBoarding, max(dateOfUsed) from LFBus group by rtNm"
    if (not.equal $last.body.result (list.new)) {"type":"success","result":$last.body.result$}
  exit
  on /api/reserve_Bus
    busNum = $data.body.contents.bus_num
    pNum = $data.body.contents.p_num
    debug busNum $busNum
    debug pNum $pNum
    index = (service xmlParser $busNum)
    debug idx $index
    service xmlParser_tagName plainNo$pNum$ $index
    plainNo1 = $last
    debug plnNo $plainNo1
    local_time = time.local "YYYY-MM-DD HH:MI:SS"
    service orientdb_rest "SELECT isBoarding FROM LFBus where plainNo=\"$plainNo1$\""
    isBoarding = $last.body.result
    debug ABC $isBoarding
    if (is.equal (list.length $isBoarding) (integer 0)) (do (service orientdb_rest "INSERT INTO LFBus CONTENT {'dateOfUsed':'$local_time$', 'rtNm':'$busNum$', 'plainNo':'$plainNo1$', 'isBoarding':'true'}") (return {"type":"success","result":$last.body.result$}))
    if (text.contains $isBoarding "false") (do (service orientdb_rest "UPDATE LFBus SET isBoarding='true' where plainNo='$plainNo1$'") {"plainNo":"$plainNo1$"}) ("true")
    debug result $last
  exit
  on /api/cancel_Bus
    busNum = $data.body.contents.bus_num
    pNum = $data.body.contents.p_num
    debug busNum $busNum
    debug pNum $pNum
    index = (service xmlParser $busNum)
    debug idx $index
    service xmlParser_tagName plainNo1 $index
    plainNo1 = $last
    debug plnNo $plainNo1
    local_time = time.local "YYYY-MM-DD HH:MI:SS"
    service orientdb_rest "SELECT isBoarding FROM LFBus where plainNo=\"$plainNo1$\""
    isBoarding = $last.body.result
    debug ABC $isBoarding
    if (is.equal (list.length $isBoarding) (integer 0)) () (do (service orientdb_rest "UPDATE LFBus SET isBoarding='false' where plainNo='$plainNo1$'") (return {"type":"success","result":$last.body.result$}))
    debug result $last
  exit
  type http server
  port 8888
exit

interface websocket_server
  port 8081
  type ws server
  on connect respond (service init)
exit

timer update_50sec
  interval 100000
  on start
    service get_low_bus_data
    service send_data_to_ws
  exit
exit

run (do (workspace.property.write a 1) (while (is.equal (service xmlParser_checker $workspace.a 501) true) (workspace.property.write a (add $workspace.a 1))))
run (do (a = 1) (while (is.equal (service xmlParser_checker $a 501) true) ($a = add $a 1)))
