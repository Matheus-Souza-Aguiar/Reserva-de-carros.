import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import psycopg2


app = FastAPI()

host = 'localhost'
database = 'ReservaCarros'
username = 'postgres'
pwd = 'root'
port_id = '5432'

conn = psycopg2.connect(
    host=host,
    dbname=database,
    user=username,
    password=pwd,
    port=port_id)

cursor = conn.cursor()

origins = ['http://127.0.0.1:5500'] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

) 

class Cars(BaseModel):
    idcar: int = None
    model: str = None
    board: str = None
    year:  str = None
    state: str = 'disponivel' 

class ReservedCar(BaseModel):
    id_car: int = None
    reserve_outset: str = None
    reserve_last: str = None


@app.post('/cadastro')
def reservar(cars: Cars):    
    
    registration = f"""INSERT INTO cars (modelCAr, boardCar, yearCar, stateCar) VALUES ('{cars.model}', '{cars.board}', '{cars.year}', '{cars.state}')"""
    
    try:
        cursor.execute(registration)
        conn.commit()
        return cars
    except:
        return {'Erro': 'Por favor conferir os dados do carro.'}


@app.post('/consulta_reserva')
def reserved_car(reservedCar: ReservedCar):
    list_True_False = []
    ids = []
    reservedCar.reserve_outset = datetime.datetime.strptime(reservedCar.reserve_outset, '%d/%m/%Y %H:%M')
    reservedCar.reserve_last = datetime.datetime.strptime(reservedCar.reserve_last, '%d/%m/%Y %H:%M')
    
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
        if reservedCar.reserve_outset > res[2]:

            if reservedCar.reserve_outset > res[3]:
                true = True
                list_True_False.append(true)

            elif reservedCar.reserve_outset < res[3]:
                
                ids.append(res[0])
                false = False
                list_True_False.append(false)


        elif reservedCar.reserve_outset < res[2]:
            if reservedCar.reserve_last < res[2]:
                true = True
                list_True_False.append(true)

            elif reservedCar.reserve_last > res[2]:
                
                ids.append(res[0])
                false = False
                list_True_False.append(false)

        elif reservedCar.reserve_outset == res[2]:
            
            ids.append(res[0])
            false = False
            list_True_False.append(false)

        elif reservedCar.reserve_last == res[3]:
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
        return {'msg': 'Sem vaga, informe outra data'}
    else:
      if False in list_True_False:

            if len(ids1) > 1:
                car = []
                check = f"""SELECT cars.idcar, cars.modelcar, cars.yearcar
                            FROM cars
                            WHERE cars.idcar NOT IN {ids1} """
                cursor.execute(check)
                list_car_reserve = cursor.fetchall()
                for cars in list_car_reserve:
                    car.append(cars)
                
                return car

            elif len(ids1) == 1:
                car = []
                ent = ids1[0]
                ids1 = int((ent))
                check = f"""select cars.idcar, cars.modelcar, cars.yearcar
                            from cars
                            WHERE cars.idcar <> {ids1} """
                
               
                cursor.execute(check)
                list_car_reserve = cursor.fetchall()
                for cars in list_car_reserve:
                    car.append(cars)
                
                return car
                           
            elif len(ids1) == 0:
                return {'msg:' 'Sem vaga para essa data'}                      
      
      else:
        car = []
        check = """SELECT cars.idcar, cars.modelcar, cars.yearcar
                                       FROM cars """
        cursor.execute(check)
        list_car_reserve = cursor.fetchall()
        for cars in list_car_reserve:
            car.append(cars)
        
        try:
            return car
        except:
            return {'Erro': 'Verificar dados de reserva'}
        


@app.post('/faz_reserva')
def checkout(reservedCar: ReservedCar):
    
    reservedCar.reserve_outset = datetime.datetime.strptime(reservedCar.reserve_outset, '%d/%m/%Y %H:%M')
    reservedCar.reserve_last = datetime.datetime.strptime(reservedCar.reserve_last, '%d/%m/%Y %H:%M')
    
    data_now = datetime.datetime.now()
    check = f"""select reservedcar.reserveoutset, reservedcar.reservelast
                 from cars
                 INNER JOIN reservedcar
                 ON  cars.idcar = reservedcar.idCar 
				 WHERE 
				 reservedcar.reservelast > '{data_now}'  AND 
				 cars.idcar = {reservedCar.id_car}"""

    list_true_false = []
    cursor.execute(check)
    list_car_reserve = cursor.fetchall()
    for res in list_car_reserve:
        if reservedCar.reserve_outset > res[0]:

            if reservedCar.reserve_outset > res[1]:
                true = True
                list_true_false.append(true)

            elif reservedCar.reserve_outset < res[1]:
                false = False
                list_true_false.append(false)

        elif reservedCar.reserve_outset < res[0]:

            if reservedCar.reserve_last < res[0]:
                true = True
                list_true_false.append(true)

            elif reservedCar.reserve_last > res[0]:
                false = False
                list_true_false.append(false)

        elif reservedCar.reserve_outset == res[0]:
            true = False
            list_true_false.append(true)

        elif reservedCar.reserve_last == res[1]:
            false = False
            list_true_false.append(false)

    if False in list_true_false:
        return{'msg': 'sem vaga'}
    else:
        
        try:
            registration = f"""INSERT INTO Reservedcar(idcar, reserveOutset, reserveLast) VALUES ({reservedCar.id_car}, '{reservedCar.reserve_outset}', '{reservedCar.reserve_last}');"""
            cursor.execute(registration)
            conn.commit()
            return {'Reserva inicial': reservedCar.reserve_outset, 'Reserva Final': reservedCar.reserve_last, 'Id do carro escolhido': reservedCar.id_car}
        except:
            return {'Erro': 'Verificar dados de reserva (id)'}



@app.post('/check_board')
def check_board(cars: Cars):
    car = []
    check = f""" select * 
                from cars 
                where boardcar = '{cars.board}' """
    cursor.execute(check)
    list_car_reserve = cursor.fetchall()
    for cars in list_car_reserve:
        car.append(cars)
    return car




@app.get('/listar_carro')
def listar_carro():
    car = []
    check = """SELECT cars.idcar, cars.modelcar, cars.yearcar, cars.statecar
                                       FROM cars 
                                       order by  idcar  ASC """
    cursor.execute(check)
    list_car_reserve = cursor.fetchall()
    for cars in list_car_reserve:
        car.append(cars)
    return car


@app.post('/update_car')
def update_state(cars: Cars):
    
    try:
        registration = f"""update cars 
                        set statecar = '{cars.state}'
                        where boardcar = '{cars.board}'"""

        cursor.execute(registration)
        conn.commit()
        car = []
        check = f""" select * 
                from cars 
                where boardcar = '{cars.board}' """
        cursor.execute(check)
        list_car_reserve = cursor.fetchall()
        for cars in list_car_reserve:
            car.append(cars)

        return car
    except:
        return {'msg': 'Não encontrado'}    



@app.post('/delete_reserve')
def delete_reserve(reservedCar: ReservedCar):

    try:
        registration = f"""delete from reservedcar 
                        where  idreservation  = {reservedCar.id_car}"""
        
        cursor.execute(registration)
        conn.commit()
        return {'msg': 'deu certo'}                   
    except:
       return {'msg': 'deu errado'}   
