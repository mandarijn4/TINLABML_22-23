import csv

class CsvWriter():
    def write_csv_file(dict_laptime, dict_angle, dict_speed, dict_track, dict_steer, dict_accel, dict_break, dict_trackpos):
    # def write_csv_file(dict_angle, dict_speed, dict_track, dict_steer, dict_accel):
        print("write csv file")
        csv_columns = ['lapTime', 'angle', 'trackPos', 'speed', 'track', 'steer', 'accel', 'brake']
        with open('data.csv', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(csv_columns)
            # data = list(zip(dict_angle, dict_speed, dict_track, dict_steer))
            data = list(zip(dict_laptime, dict_angle, dict_trackpos, dict_speed, dict_track, dict_steer, dict_accel, dict_break))
            # data = list(zip(dict_angle, dict_speed, dict_track, dict_steer, dict_accel))
            for row in data:
                row = list(row)
                writer.writerow(row)