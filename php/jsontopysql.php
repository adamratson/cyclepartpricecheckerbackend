<?php
/**
 * Created by PhpStorm.
 * User: Adam
 * Date: 10/03/2016
 * Time: 20:35
 */

require("mysqlinfo.php");

$jsonfiles = array("bikediscountprodlist.json", "wiggleprodlist.json", "crcprodlist.json");

if (time()-filemtime("exchangerates.json") > 86400) {
    file_put_contents("exchangerates.json", fopen("http://openexchangerates.org/api/latest.json?app_id=c5c4680ca78d4ff5ac5ae07398bdfb1a", 'r'));
}

$exchangeratesarray = json_decode(file_get_contents("exchangerates.json"), true);
$gbptoeur = (1/$exchangeratesarray["rates"]["GBP"])*$exchangeratesarray["rates"]["EUR"];

$conn = new PDO('mysql:host=localhost;dbname=cyclepartpricechecker_db;charset=utf8', $sqlusername, $sqlpassword, array(PDO::ATTR_EMULATE_PREPARES => false, PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION));

$stmt = $conn->prepare("DELETE FROM wiggleprods");
$stmt->execute();
$stmt = $conn->prepare("DELETE FROM bikediscountprods");
$stmt->execute();
$stmt = $conn->prepare("DELETE FROM crcprods");
$stmt->execute();

foreach($jsonfiles as $jsonfile){
    $json = file_get_contents("../json/".$jsonfile);
    $jsonprods = json_decode($json, true);
    foreach($jsonprods as $jsonbrands){
        foreach($jsonbrands as $jsonprod){
            if ($jsonfile == "wiggleprodlist.json") {
                $stmt = $conn->prepare("INSERT INTO wiggleprods (prodname, produrl, prodpricegbp, prodpriceeur, brand) VALUES (:jsonprodname, :jsonprodurl, :jsonprodpricegbp, :jsonprodpriceeur, :jsonbrand)");
            } elseif ($jsonfile == "bikediscountprodlist.json"){
                $stmt = $conn->prepare("INSERT INTO bikediscountprods (prodname, produrl, prodpricegbp, prodpriceeur, brand) VALUES (:jsonprodname, :jsonprodurl, :jsonprodpricegbp, :jsonprodpriceeur, :jsonbrand)");
            } elseif ($jsonfile == "crcprodlist.json"){
                $stmt = $conn->prepare("INSERT INTO crcprods (prodname, produrl, prodpricegbp, prodpriceeur, brand) VALUES (:jsonprodname, :jsonprodurl, :jsonprodpricegbp, :jsonprodpriceeur, :jsonbrand)");
            }
            $stmt->bindValue(":jsonprodname", $jsonprod["prodname"]);
            $stmt->bindValue(":jsonprodurl",$jsonprod["produrl"]);
            if (isset($jsonprod["prodpricegbp"])) {
                $stmt->bindValue(":jsonprodpricegbp", $jsonprod["prodpricegbp"]);
                $stmt->bindValue(":jsonprodpriceeur", $jsonprod["prodpricegbp"]*$gbptoeur);
            } else {
                $stmt->bindValue(":jsonprodpriceeur", $jsonprod["prodpriceeur"]);
                $stmt->bindValue(":jsonprodpricegbp", $jsonprod["prodpriceeur"]/$gbptoeur);
            }
            $stmt->bindValue(":jsonbrand", array_search($jsonbrands, $jsonprods));
            $stmt->execute();
        }
    }
}

$conn = null;