import csv

class CsvWriter():
    def write_csv_file(dict_angle, dict_speed, dict_track, dict_steer, dict_accel, dict_break):
    # def write_csv_file(dict_angle, dict_speed, dict_track, dict_steer, dict_accel):
        print("write csv file")
        csv_columns = ['angle', 'speed', 'track', 'steer', 'accel', 'break']
        with open('data.csv', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(csv_columns)
            # data = list(zip(dict_angle, dict_speed, dict_track, dict_steer))
            data = list(zip(dict_angle, dict_speed, dict_track, dict_steer, dict_accel, dict_break))
            # data = list(zip(dict_angle, dict_speed, dict_track, dict_steer, dict_accel))
            for row in data:
                row = list(row)
                writer.writerow(row)