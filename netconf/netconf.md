## NETCONF / RESTCONF | YANG

### NETCONF (IOS_XE)
----
#### Для работы netconf на IOS XE, требуется:
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

Для того что бы узнать иерархию и  список доступных ключей в xml-файле, требуется скачать model-yang файлы с [репозитория](https://github.com/YangModels/yang) и открыть требуемый файл через **pyang**.
Структура файла указана в ключе `<native>`, в примере выше это *Cisco-IOS-XE-native*.

Если допустить ошибку только в одном контейнере xml файла, вся конфигурация не будет применена.

Ключ `<lock>` блокирует изменения на оборудовании, соответственно `<unlock>` - разблокирует

Все очень подробно написано в [RFC6241](https://tools.ietf.org/html/rfc6241)
