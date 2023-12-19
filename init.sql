create DATABASE IF NOT EXISTS ss;
use ss;

CREATE TABLE IF NOT EXISTS `ss`.`user` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NULL,
  `email` VARCHAR(45) NULL,
  `password` VARCHAR(100) NULL,
  `username` VARCHAR(45) NULL,
  PRIMARY KEY (`ID`));

CREATE TABLE IF NOT EXISTS `ss`.`room` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `number` VARCHAR(45) NULL,
  `latitude` FLOAT NULL,
  `longitude` FLOAT NULL,
  `maxvolume` INT NULL,
  `note` VARCHAR(45) NULL,
  PRIMARY KEY (`ID`));

CREATE TABLE IF NOT EXISTS `ss`.`seat` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `roomid` VARCHAR(45) NULL,
  `number` VARCHAR(45) NULL,
  `ischarge` VARCHAR(45) NULL,
  `isdisabled` VARCHAR(45) NULL,
  `freetime` VARCHAR(45) NULL,
  `usingtime` VARCHAR(45) NULL,
  `bookedtime` VARCHAR(45) NULL,
  PRIMARY KEY (`ID`));

CREATE TABLE IF NOT EXISTS `ss`.`booking` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `seatid` VARCHAR(45) NULL,
  `userid` VARCHAR(45) NULL,
  `booktime` VARCHAR(45) NULL,
  `starttime` VARCHAR(45) NULL,
  `finishtime` VARCHAR(45) NULL,
  `isdefault` VARCHAR(45) NULL,
  `iscancel` VARCHAR(45) NULL,
  `bookingcol` VARCHAR(45) NULL,
  PRIMARY KEY (`ID`));