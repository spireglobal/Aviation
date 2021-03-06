import csv, requests, datetime, time, json, timeit
from xml.dom import minidom


#counter of target_updates
tu_count = 0
terr_count = 0
sat_count = 0

#reads data from XML file
class Xml:

    def __init__(self, xmlfile, tagname):
        self.xml = xmlfile
        self.tagname = tagname

    def xml_file(self):
        xmldoc = minidom.parse(self.xml)
        xmlitems = xmldoc.getElementsByTagName(self.tagname)
        #append xmlnodes into xml_params
        xml_params = [item.childNodes[0].nodeValue for item in xmlitems]
        xml_params.append(runtime)
        return xml_params

#class to access Spire Datastream API
#inherits from XML
class Stream():

    def __init__(self, url, token, timeout, file_handler):
        self.url = url
        self.token = token
        self.timeout = int(timeout)
        self.file_handler = file_handler

    @staticmethod
    #will return time
    def get_time():
        time_now = datetime.datetime.now()
        time_converted = time_now.strftime("%m-%d-%Y_%H-%M-%S_%p")
        return time_converted

    #call datastream and output to new file
    def call_stream(self):
        try:
            #paramaters for call
            headers = {'Content-Type': 'application/json','Authorization': 'Bearer {0}'.format(self.token)}
            #using start_time multiple times throughout method
            start_time = time.time()
            timeout = start_time + self.timeout
            s = requests.Session()

            #calling datastream
            with s.get(self.url, headers=headers, stream=True, timeout=None) as r:
                with open('ds_json/' + 'ds:' + self.get_time() + '.json', self.file_handler) as json_file:

                    #global declaration
                    global tu_count
                    FILENAME.append(json_file.name)

                    #reading through JSON hashtables
                    for line in r.iter_lines(decode_unicode=True):
                        tu_count += 1
                        if time.time() < timeout:

                            #msg is for further parsing, use loads
                            msg = json.loads(line)
                            for item in msg:
                                if item == 'stream_token':
                                    STREAM_TOKEN.append(msg)
                                    print(STREAM_TOKEN)

                            #returned to list for CSV use
                            try:
                                data = msg['target']
                                JSONDict.append(data)

                                #dumps is for pretty print
                                json_pprint = json.dumps(msg, ensure_ascii=False, indent=4)
                                json_file.write(json_pprint)
                                if pp_print_stream == 'Y':
                                    print(json_pprint)
                                elif pp_print_stream == 'N':
                                    pass
                                else:
                                    print(json_pprint)
                            except (AttributeError, KeyError, TypeError, ValueError) as e:
                                pass
                        else:
                            r.close()
        except (AttributeError, KeyError, json.decoder.JSONDecodeError, TypeError, ValueError) as e:
            timeout_record.append(time.time() - start_time)
            pass

#class for Dictionary object that holds our parsed JSON string objects**
#inherit attributes from Stream
class Csv:

    #attributes for class
    def __init__(self, JSONDict):
        self.JSONDict= JSONDict

    def json2csv(self):
        try:
            time_now = datetime.datetime.now()
            time_converted = time_now.strftime("%m-%d-%Y_%H-%M-%S_%p")

            with open( 'ds_csv/' +'ds:' +  time_converted +'.csv', 'w', newline='') as csv_file:
                fieldnames=['icao_address', 'timestamp', 'latitude', "longitude", "altitude_baro", "heading",
                "ground_speed", "vertical_rate",'squawk_code' ,"on_ground", "callsign",  "tail_number", "collection_type",
                "source", "flight_number", "origin_airport_iata", "destination_airport_iata"]
                csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                csv_writer.writeheader()
                for key in self.JSONDict:
                        csv_writer.writerow(key)
        except json.decoder.JSONDecodeError:
            pass

#inherit attribute from Csv
class Statistics(Csv):

    #attributees for class
    def __init__(self, terrestrial, satellite, total):
        super().__init__(JSONDict)
        self.terrestrial = terrestrial
        self.satellite = satellite
        self.total = total

    def statistics(self):

        #global declarations for assignments
        global terr_count
        global sat_count
        global tu_count

        #use map here
        for key in self.JSONDict:
            for item in key:
                if item == 'collection_type' and key[item] == 'terrestrial':
                    terr_count += 1
                elif item == 'collection_type' and key[item] == 'satellite':
                    sat_count += 1


if __name__ == '__main__':

    #global variable for getting filename created at callstream
    FILENAME = []
    #list for JSON string lines
    JSONDict = []
    #list for stream_token positions
    STREAM_TOKEN = []
    #timeout record
    timeout_record = []

    #program runtime as input
    runtime = int(input('Enter program timeout, in seconds: '))
    timeout_record.append(runtime)
    output_csv = input('Do you want a CSV output file? (Y/N) : ')
    pp_print_stream = input('Do you want to see target_updates printed to command line during call? (Y/N) : ')

    #instance of XML file reading
    xml_arg = Xml('ds.xml', 'item')

    #instance of stream arguments
    xml_args_pass = xml_arg.xml_file()
    stream_call = Stream(xml_args_pass[0], xml_args_pass[1], runtime, 'w')
    stream_call.call_stream()

    #instance of Statistics
    statistics_call = Statistics(terr_count, sat_count, tu_count)
    statistics_call.statistics()
    #conditional printout for CSV file
    if output_csv == 'Y':
        #instance of Csv
        csv_call = Csv(JSONDict)
        csv_call.json2csv()
    elif output_csv == 'N':
        pass

    #print statements for statistics
    print('Stream ran for: {} seconds'.format(timeout_record[0]))
    print('Total Target Updates: {}'.format(tu_count))
    print('Terrestrial Target Updates: {}'.format(terr_count))
    print('Satellite Target Updates: {}'.format(sat_count))
    print('Stream Token Updates:', tu_count - (terr_count + sat_count))
    print('Query Paramters: {}'.format(xml_args_pass))
