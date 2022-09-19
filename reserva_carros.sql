CREATE TABLE cars(
       idCar SERIAL PRIMARY KEY,
	   modelCar VARCHAR(45) NOT NULL,
	   boardCAr VARCHAR(45) NOT NULL,
	   yearCar VARCHAR(4) NOT NULL,
       stateCar VARCHAR(45) NOT NULL
);

INSERT INTO cars (modelCAr, boardCar, yearCar, stateCar) VALUES ('Voyage', 'HMH58H', '2019', 'Disponivel');
INSERT INTO cars (modelCAr, boardCar, yearCar, stateCar) VALUES ('Gol G4', 'OJ8POS', '2014', 'Disponivel');
INSERT INTO cars (modelCAr, boardCar, yearCar, stateCar) VALUES ('Prisma LTZ ', 'QWOJ57', '2011', 'Disponivel');
INSERT INTO cars (modelCAr, boardCar, yearCar, stateCar) VALUES ('S10', 'QWI50S',  '2022', 'Disponivel');


CREATE TABLE ReservedCar(
    idreservation SERIAL,   
	idCar integer,
	reserveOutset TIMESTAMP NOT NULL,
	reserveLast TIMESTAMP NOT NULL,
 	PRIMARY KEY (idCar, idreservation),
	FOREIGN KEY (idCar) references cars (idCar)
);
	
SELECT *
FROM cars;

SELECT *
FROM reservedCar;




