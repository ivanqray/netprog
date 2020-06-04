## NETCONF / RESTCONF | YANG

### NETCONF (IOS_XE)
----
**Для работы netconf на IOS XE, требуется:**
* Включить SSH 
* Включить netconf:  ```(config)# netconf-yang```
* Проверить включение всех связанных служб (должны быть в состоянии Running):  ```show platform software yang-management process```

По умолчанию netconf использует `830` `tcp` порт.
Проверить его работу можно, подключившись к оборудованию по SSH через CLI:
```ssh cisco@10.10.10.10 -p 830 -s netconf```

При удачном подключении к оборудованию, клиент получит `hello` (список `capabilities` доступных на данном оборудовании), в ответ требуется отправить список доступных `capabilities` клиента.
После подключения, hello-сообщение от оборудования должно содержать параметр `<session-id>` иначе клиент разорвет сессию, и наоборот если клиент отправит серверу сообщение с `<session-id>`, сервер разорвет сессию. Ответное hello-сообщение не должно содержать параметр `<session-id>`.

**Пример ответного hello-сообщения:**
```
<?xml version="1.0" encoding="UTF-8"?> 
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<capabilities>
<capability>urn:ietf:params:netconf:base:1.0</capability>
</capabilities>
</hello>]]>]]>
```

* ```<?xml version="1.0" encoding="UTF-8"?>```  - стандартный xml заголовок
* ```<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">``` - hello xmlns полученный от сетевого оборудования
* ```<capability>urn:ietf:params:netconf:base:1.0</capability>``` -  "urn:ietf:params:netconf:base:1.1” (base:1.0) является обязательным capability (при большом количестве каждый перечисляется между ключами <capability></capability>)
* ```</hello>]]>]]>``` - конец сообщения сопровождается символами ```]]>]]>```

После обмена hello-сообщениями, оборудование может обмениваться rpc-сообщениями `<rpc></rpc>`. Базовая реализация протокола включает следующие виды запросов: 
`<get>`, `<get-config>`, `<edit-config>`, `<copy-config>`, `<delete-config>`, `<lock>`, `<unlock>`, `<close-session>`, `<kill-session>`.  

**Пример запроса running-конфигурации:**
```
<?xml version="1.0"?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="38">
<get-config>
<source>
<running/>
</source>
</get-config>
</rpc>]]>]]>
```

`<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="38">` - xmlns полученный при обмене hello-сообщениями.

**message-id**  - обязательный элемент, указывающий на номер сесси со стороны клиента, сервер не обрабатывает это значение а лишь использует его в `<rpc-reply>`

**Пример изменения конфигурации:**
```
<?xml version="1.0"?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="38">
<edit-config>
<target>
<running/>
</target>
<config>
<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
		<hostname>RXE1-NETCONF</hostname>
		<username>
			<name>telecom</name>
			<privilege>15</privilege>
			<password>
				<encryption>0</encryption>
				<password>Per0Jn2#</password>
			</password>
		</username>
</native>
</config>
</edit-config>
</rpc>]]>]]>
```

Для того что бы узнать иерархию и  список доступных ключей в xml-файле, требуется скачать model-yang файлы с [репозитория](https://github.com/YangModels/yang) и открыть требуемый файл через **pyang** *(ex. pyang -f tree model.yang)*.
Структура файла указана в ключе `<native>`, в примере выше это *Cisco-IOS-XE-native*.

Если допустить ошибку только в одном контейнере xml файла, вся конфигурация не будет применена.

Ключ `<lock>` блокирует изменения на оборудовании, соответственно `<unlock>` - разблокирует

Все очень подробно написано в [RFC6241](https://tools.ietf.org/html/rfc6241)

**Writable-Running Capability**

Если оборудование поддерживает *writable-running capability*, значит есть возможность использовать `<edit-config>` и `<copy-config>` операции где изменения применяются в `<running>` конфигурацию.

**Пример writable-running capability:**
`urn:ietf:params:netconf:capability:writable-running:1.0`

**Augment**
Внутри стандартного xmls могут быть вложенные xmls ссылающиеся на другие модели, например, для добавления ospf на сам интерфейс а не через router ospf  потребуется внтури описания интерфейса сослаться на другую модель. В нашем случае это *Cisco-IOS-XE-OSPF*
В описании файла будет указана необходимая вложенность для добавления ospf на самом интерфейсе.
Вывод строки файла Cisco-IOS-XE-OSPF.yang:
`augment /ios:native/ios:interface/ios:Loopback/ios:ip:`

Что указывает на вложенность:
```
<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                                                             <interface>
            															 <Loopback>
            																		 <ip> 
                                                          <ospf xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ospf">    
		                                                                             </ip>
																		   </Loopback>
															  <interface>
													</native>
```

**Пример конфигурации интерфейса:**
```
<?xml version="1.0"?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="38">
<edit-config>
<target>
<running/>
</target>
<config>
<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
	<interface>
		<Loopback>
			<name>1</name>
			<description>my first loopback</description>
			<ip>
				<primary>
				<address>169.100.85.1</address>
				<mask>255.255.255.255</mask>
				</primary>
				<ospf xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ospf">
						<process-id>
							<id>1</id>
							<area>1</area>
						</process-id>
				</ospf>
			</ip>
		</Loopback>	
	</interface>
</native>
</config>
</edit-config>
</rpc>]]>]]>
```

**GET**

Для получения всех статусов интерфейсов, arp-таблиц и т.п можно использовать следующий запрос:
```
<?xml version="1.0"?>
	 <rpc message-id="101"
          xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
       <get/>
     </rpc>]]>]]>
```

В yang-моделях файлы с описанием структуры запроса называются *‘modelname’-oper.yang*

**Subtree Filtering**

`xml <filter type="subtree">`, это механизм выборки конкретного ключа в `<rpc-reply>` для операций
 `<get>` или `<get-config>`.

**Пример запроса:**
```
<?xml version="1.0"?>
<rpc message-id="101"
xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<get>
<filter type="subtree">
<device-hardware-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-device-hardware-oper">
<device-hardware/>
</device-hardware-data>
</filter>
</get>
</rpc>]]>]]>
```

**Дополнительные параметры внутри контейнеров**

`<… configuration=”replace”>` - замена контейнера
> *“create”* – добавляет конфигурацию если ее нет, в противном случае возвращает <rpc-error>
> *“replace”* – заменяет конфигурацию контейнера если она есть, в противном случает создает ее. В отличии от <copy-config>, который заменяет конфигурацию только если она существует.
> *“delete”* -  удаляет конфигурацию если она есть, в противном случае возвращает <rpc-error>
> *“remove”* - удаляет конфигурацию если она есть, в противном случае команда игнорируется
> *“merge”* – добавляет конфигурацию. (Действие по умолчанию)

