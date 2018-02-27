# different
Database lab 4

UPDATE staff SET salary = (salary * 1.1)
WHERE position1 = 'Assistant';

SELECT * FROM staff
WHERE sex = 'M'
ORDER BY dob ASC;

SELECT * FROM propertyforrent
WHERE rooms >=3 AND rooms <=4
ORDER BY rent;

SELECT * FROM staff
WHERE lname LIKE 'B%';

SELECT * FROM client1
WHERE telNo LIKE '%1%1%1%';

SELECT * FROM viewing 
WHERE comment1 != " ";

SELECT AVG(salary) AS 'SalaryAVG' FROM staff;

SELECT branchNo, COUNT(staffNo) FROM staff
GROUP BY branchNo;

SELECT branchNo, COUNT(staffNo), 
MIN(salary) AS 'MinSalary', 
AVG(salary) AS 'AvgSalary',
MAX(salary) AS 'MaxSalary' FROM staff
GROUP BY branchNo;

SELECT branchNo, sex, COUNT(staffNo) AS 'Staff',
MIN(salary) AS 'MinSalary', 
AVG(salary) AS 'AvgSalary',
MAX(salary) AS 'MaxSalary' FROM staff
GROUP BY branchNo, sex;

SELECT *,MIN(rent) FROM propertyforrent
WHERE rooms = 4;

SELECT type1, MAX(rent) AS  'Max $', MIN(rent) AS 'Min $' FROM propertyforrent
GROUP BY type1;

SELECT * FROM propertyforrent
WHERE city = 'Aberdeen';

SELECT city, COUNT(propertyNo) AS 'count' FROM propertyforrent
GROUP BY city;

SELECT * FROM viewing 
WHERE comment1 = " ";

SELECT * FROM propertyforrent
WHERE propertyNo LIKE "PG%" AND type1 = 'House';

SELECT * FROM viewing
WHERE viewDate LIKE '2004-%-%';

SELECT * FROM staff
WHERE staffNo IN (SELECT staffNo FROM propertyforrent WHERE staffNo != ' ');

SELECT * FROM client1
WHERE clientNo IN (SELECT clientNo FROM viewing);
			
SELECT type1, COUNT(type1) AS 'Count' FROM propertyforrent
WHERE type1 IN (SELECT prefType FROM client1)
GROUP BY type1;

UPDATE propertyforrent SET type1 = 'House';
WHERE type1 IN (SELECT prefType FROM client1 WHERE prefType = 'House') AND rent <= IN (SELECT maxrent FROM client1 WHERE maxrent <= 600);
