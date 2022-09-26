import datetime
import pandas as pd
import pyodbc
import psycopg2

host = 'localhost'
database = 'ReservaCarros'
username = 'postgres'
pwd = 'AAAaaa123'
port_id = '5432'

conn = psycopg2.connect(
    host=host,
    dbname=database,
    user=username,
    password=pwd,
    port=port_id)

cursor = conn.cursor()


def car_registration():
    print('Cadastrar veículo.\nTodos os campos devem ser prenchidos corretamente\n')
    model = input('Por favor informe o modelo do carro?  ')
    board = input('Informe a placa do carro?  ')
    year = input('Informe o ano do carro? ')
    state = input('O carro está disponivel ou na manutenção? Disponivel(d)/manutenção(m):  ')
    if state == 'd':
        state = 'Disponivel'
    elif state == 'm':
        state = 'Manutenção'
    check = input(
        f'\nO carro com as seguintes informações, Modelo: {model}, placa: {board}, ano: {year}, está {state}.\nVocê confirma essas informações? sim(s)/não(n)? ')
    if check == 's':
        print('Carro registrado')
        registration = f"""INSERT INTO cars (modelCAr, boardCar, yearCar, stateCar) VALUES ('{model}', '{board}', '{year}', '{state}')"""
        cursor.execute(registration)
        conn.commit()
        return main()
    elif check == 'n':
        print('As infomações serão alteradas')
        return car_registration()


def reserve_car():
    print('Reserva de carros\n')
    reserve_outset = input('Informe o dia e a hora em que você ira reservar o carro? DD/MM/YYY HH:MM: ')
    reserve_last = input('Informe até que dia e hora pretende ter o carro reservado? DD/MM/YYY HH:MM: ')
    confer = input(
        f'\nVocê pretende iniciar sua reserva em {reserve_outset} e finalizar em {reserve_last}? sim(s)/não(n): ')
    if confer == 's':
        reserve_outset = datetime.datetime.strptime(reserve_outset, '%d/%m/%Y %H:%M')
        reserve_last = datetime.datetime.strptime(reserve_last, '%d/%m/%Y %H:%M')
        print('\nVamos verificar se tem vaga disponivel para essa data')
        return check_cars_in_reverse(reserve_outset, reserve_last)
    elif confer == 'n':
        return reserve_car()


def checkout(idcar, reserve_outset, reserve_last):
    data_now = datetime.datetime.now()
    check = f"""select reservedcar.reserveoutset, reservedcar.reservelast
                 from cars
                 INNER JOIN reservedcar
                 ON  cars.idcar = reservedcar.idCar 
				 WHERE 
				 reservedcar.reservelast > '{data_now}'  AND 
				 cars.idcar = {idcar}"""

    list_true_false = []
    cursor.execute(check)
    list_car_reserve = cursor.fetchall()
    for res in list_car_reserve:
        if reserve_outset > res[0]:

            if reserve_outset > res[1]:
                true = True
                list_true_false.append(true)

            elif reserve_outset < res[1]:
                false = False
                list_true_false.append(false)

        elif reserve_outset < res[0]:

            if reserve_last < res[0]:
                true = True
                list_true_false.append(true)

            elif reserve_last > res[0]:
                false = False
                list_true_false.append(false)

        elif reserve_outset == res[0]:
            true = False
            list_true_false.append(true)

        elif reserve_last == res[1]:
            false = False
            list_true_false.append(false)

    if False in list_true_false:
        print('Sem vaga para essa data')
        return reserve_car()
    else:
        registration = f"""INSERT INTO Reservedcar(idcar, reserveOutset, reserveLast) VALUES ({idcar}, '{reserve_outset}', '{reserve_last}');"""
        cursor.execute(registration)
        conn.commit()
        print('Sua reserva foi registrada!')
        return final()


def check_cars_in_reverse(reserve_outset, reserve_last):
    reserve_cars = []
    list_True_False = []
    ids = []
    data_now: datetime = datetime.datetime.now()
    check = f"""select reservedcar.idcar, cars.modelcar, reservedcar.reserveoutset, reservedcar.reservelast
                     from cars
                     INNER JOIN reservedcar
                     ON  cars.idcar = reservedcar.idCar 
    				 WHERE 
    				 reservedcar.reservelast > '{data_now}'  """
    cursor.execute(check)
    list_car_reserve = cursor.fetchall()
    for res in list_car_reserve:
        if reserve_outset > res[2]:

            if reserve_outset > res[3]:
                true = True
                list_True_False.append(true)

            elif reserve_outset < res[3]:
                ids.append(res[0])
                reserve_cars.append(res)
                false = False
                list_True_False.append(false)


        elif reserve_outset < res[2]:
            if reserve_last < res[2]:
                true = True
                list_True_False.append(true)

            elif reserve_last > res[2]:
                ids.append(res[0])
                reserve_cars.append(res)
                false = False
                list_True_False.append(false)

        elif reserve_outset == res[2]:
            ids.append(res[0])
            reserve_cars.append(res)
            false = False
            list_True_False.append(false)

        elif reserve_last == res[3]:
            reserve_cars.append(res)
            false = False
            list_True_False.append(false)

    ids1 = tuple((ids))

    check = f"""select count (idcar)
                from cars; """
    cursor.execute(check)
    list_car_reserve = cursor.fetchall()
    car = list_car_reserve[0]
    car1 = car[0]
    if len(ids1) == car1:
        print('Sem vaga, Por favo, informe outra data')
        return reserve_car()
    else:
        if False in list_True_False:

            if len(ids1) > 1:
                option_cars_one(ids1, reserve_outset, reserve_last)

            elif len(ids1) == 1:
                option_cars_two(ids1, reserve_outset, reserve_last)

            elif len(ids1) == 0:
                print('Não tem carro disponivel para essa data')
                return reserve_car()
        else:
            option_cars_three(reserve_outset, reserve_last)


def option_cars_one(ids1, reserve_outset, reserve_last):
    print('Carros disponiveis para essa data')
    check = pd.read_sql(f"""SELECT cars.idcar, cars.modelcar, cars.yearcar
                            FROM cars
                            WHERE cars.idcar NOT IN {ids1} """, conn)
    print(check)
    idcar = input('Informe o Id do carro que deseja reservar? ')
    return check_id_car(idcar, ids1, reserve_outset, reserve_last)


def option_cars_two(ids1, reserve_outset, reserve_last):
    ent = ids1[0]
    ids1 = int((ent))
    print('Carros disponiveis para essa data')
    check = pd.read_sql(f"""select cars.idcar, cars.modelcar, cars.yearcar
                            from cars
                            WHERE cars.idcar <> {ids1} """, conn)
    print(check)
    idcar = input('Informe o Id do carro que deseja reservar? ')
    return check_id_car_option_two(idcar, ids1, reserve_outset, reserve_last)


def option_cars_three(reserve_outset, reserve_last):
    print('Carros disponiveis para essa data')
    check = pd.read_sql("""SELECT cars.idcar, cars.modelcar, cars.yearcar
                                       FROM cars """, conn)
    print(check)
    idcar = input('Informe o Id do carro que deseja reservar? ')
    return check_id_car_option_three(idcar, reserve_outset, reserve_last)


def check_id_car(idcar, ids1, reserve_outset, reserve_last):
    check_id = []
    check = (f"""SELECT cars.idcar, cars.modelcar, cars.yearcar
                 FROM cars
                 WHERE cars.idcar NOT IN {ids1} """)
    cursor.execute(check)
    list_car_id = cursor.fetchall()
    for res in list_car_id:
        id = res[0]
        idcarro = str(id)
        check_id.append(idcarro)

    if idcar in check_id:
        print('encontrado')
        return checkout(idcar, reserve_outset, reserve_last)
    else:
        print(type(check_id))
        print(type(idcar))
        print(f'Não encontrado!{idcar},{check_id}')
        return check_cars_in_reverse(reserve_outset, reserve_last)


def check_id_car_option_two(idcar, ids1, reserve_outset, reserve_last):
    check_id = []
    check = (f"""select cars.idcar, cars.modelcar, cars.yearcar
                                from cars
                               WHERE cars.idcar <> {ids1}""")
    cursor.execute(check)
    list_car_id = cursor.fetchall()
    for res in list_car_id:
        id = res[0]
        idcarro = str(id)
        check_id.append(idcarro)

    if idcar in check_id:
        print('encontrado')
        return checkout(idcar, reserve_outset, reserve_last)
    else:
        print(f'Não encontrado, Informe o id novamente, por favor!')
        return check_cars_in_reverse(reserve_outset, reserve_last)


def check_id_car_option_three(idcar, reserve_outset, reserve_last):
    check_id = []
    check = (f"""SELECT cars.idcar, cars.modelcar, cars.yearcar
                                       FROM cars""")
    cursor.execute(check)
    list_car_id = cursor.fetchall()
    for res in list_car_id:
        id = res[0]
        idcarro = str(id)
        check_id.append(idcarro)

    if idcar in check_id:
        print('encontrado')
        return checkout(idcar, reserve_outset, reserve_last)
    else:
        print(f'Não encontrado, Informe o id novamente, por favor!')
        return check_cars_in_reverse(reserve_outset, reserve_last)


def final():
    final = input('Deseja fazer voltar ao menu ou encerrar o atendimento? encerrar(e)/menu(m): ')
    if final == 'm':
        return main()
    elif final == 'e':
        return print('Até mais!')


def main():
    user_main = input('Olá, Informe a letra correspondente ao que deseja fazer\n(c) Cadastrar um veículo\n(r) fazer uma reserva\nInforme a letra: ')
    if user_main == 'c':
        return car_registration()
    elif user_main == 'r':
        return reserve_car()


main()
