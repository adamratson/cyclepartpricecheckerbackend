<?php
/**
 * Created by PhpStorm.
 * User: Adam
 * Date: 10/03/2016
 * Time: 20:35
 */

require("mysqlinfo.php");

$json = file_get_contents("../json/wiggleprodlist.json");
$jsonprods = json_decode($json, true);

$conn = new PDO('mysql:host=localhost;dbname=cyclepartpricechecker_db;charset=utf8', $sqlusername, $sqlpassword, array(PDO::ATTR_EMULATE_PREPARES => false, PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION));


foreach($jsonprods as $jsonbrands){
    foreach($jsonbrands as $jsonprod){
        $stmt = $conn->prepare('INSERT INTO wiggleprods (prodname, produrl, prodpricegbp, prodpriceeur, brand) VALUES (:jsonprodname, :jsonprodurl, :jsonprodpricegbp, :jsonprodpriceeur, :jsonbrand)');
        $stmt->bindValue(":jsonprodname", $jsonprod["prodname"]);
        $stmt->bindValue(":jsonprodurl",$jsonprod["produrl"]);
        $stmt->bindValue(":jsonprodpricegbp", $jsonprod["prodpricegbp"]);
        $stmt->bindValue(":jsonprodpriceeur",1);
        $stmt->bindValue(":jsonbrand", array_search($jsonbrands, $jsonprods));
        $stmt->execute();
    }
}

$conn = null;