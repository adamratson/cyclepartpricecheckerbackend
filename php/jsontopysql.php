<?php
/**
 * Created by PhpStorm.
 * User: Adam
 * Date: 10/03/2016
 * Time: 20:35
 */

require("mysqlinfo.php");

$prodfiles = array("bikediscountprodlist.json", "wiggleprodlist.json", "crcprodlist.json");
$brandfiles = array("bikediscountbrandlist.json", "wigglebrandlist.json", "crcbrandlist.json");

if (time()-filemtime("exchangerates.json") > 86400) {
    file_put_contents("exchangerates.json", fopen("http://openexchangerates.org/api/latest.json?app_id=c5c4680ca78d4ff5ac5ae07398bdfb1a", 'r'));
}

$exchangeratesarray = json_decode(file_get_contents("exchangerates.json"), true);
$gbptoeur = (1/$exchangeratesarray["rates"]["GBP"])*$exchangeratesarray["rates"]["EUR"];

$conn = new PDO('mysql:host=localhost;dbname=cyclepartpricechecker_db;charset=utf8', $sqlusername, $sqlpassword, array(PDO::ATTR_EMULATE_PREPARES => false, PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION));

$stmt = $conn->prepare("DELETE FROM wiggleprods");
$stmt->execute();
$stmt = $conn->prepare("DELETE FROM bdprods");
$stmt->execute();
$stmt = $conn->prepare("DELETE FROM crcprods");
$stmt->execute();
$stmt = $conn->prepare("DELETE FROM brands");
$stmt->execute();

foreach($brandfiles as $brandfile){
    $json = file_get_contents("../json/".$brandfile);
    $jsonbrands = json_decode($json, true);
    if ($brandfile == "bikediscountbrandlist.json") {
        foreach ($jsonbrands as $jsonbrand) {
            $stmt = $conn->prepare("SELECT brand, brandID FROM brands WHERE brand=:jsonbrand");
            $stmt->bindValue(":jsonbrand", array_search($jsonbrand, $jsonbrands));
            if ($stmt->execute()) {
                $fetched = $stmt->fetch(PDO::FETCH_ASSOC);
                if (isset($fetched['brand'])) {
                    $stmt1 = $conn->prepare("UPDATE brands SET bdBrandURL=:jsonurl WHERE brandID=:brandID");
                    $stmt1->bindValue(":jsonurl", $jsonbrand);
                    $stmt1->bindValue(":brandID", $fetched['brandID']);
                    $stmt1->execute();
                } else {
                    $stmt = $conn->prepare("INSERT INTO brands (brandID, brand, bdBrandURL) VALUES (null, :jsonbrand, :jsonbrandurl)");
                    $stmt->bindValue(":jsonbrand", array_search($jsonbrand, $jsonbrands));
                    $stmt->bindValue(":jsonbrandurl", $jsonbrand);
                    $stmt->execute();
                }
            }
        }
    }
    if ($brandfile == "wigglebrandlist.json") {
        foreach ($jsonbrands as $jsonbrand) {
            $stmt = $conn->prepare("SELECT brand, brandID FROM brands WHERE brand=:jsonbrand");
            $stmt->bindValue(":jsonbrand", array_search($jsonbrand, $jsonbrands));
            if ($stmt->execute()) {
                $fetched = $stmt->fetch(PDO::FETCH_ASSOC);
                if (isset($fetched['brand'])) {
                    $stmt1 = $conn->prepare("UPDATE brands SET wiggleBrandURL=:jsonurl WHERE brandID=:brandID");
                    $stmt1->bindValue(":jsonurl", $jsonbrand);
                    $stmt1->bindValue(":brandID", $fetched['brandID']);
                    $stmt1->execute();
                } else {
                    $stmt = $conn->prepare("INSERT INTO brands (brandID, brand, wiggleBrandURL) VALUES (null, :jsonbrand, :jsonbrandurl)");
                    $stmt->bindValue(":jsonbrand", array_search($jsonbrand, $jsonbrands));
                    $stmt->bindValue(":jsonbrandurl", $jsonbrand);
                    $stmt->execute();
                }
            }
        }
    }
    if ($brandfile == "crcbrandlist.json") {
        foreach ($jsonbrands as $jsonbrand) {
            $stmt = $conn->prepare("SELECT brand, brandID FROM brands WHERE brand LIKE :jsonbrand");
            $stmt->bindValue(":jsonbrand", array_search($jsonbrand, $jsonbrands));
            if ($stmt->execute()) {
                $fetched = $stmt->fetch(PDO::FETCH_ASSOC);
                if (isset($fetched['brand'])) {
                    $stmt1 = $conn->prepare("UPDATE brands SET crcBrandURL=:jsonurl WHERE brandID=:brandID");
                    $stmt1->bindValue(":jsonurl", $jsonbrand);
                    $stmt1->bindValue(":brandID", $fetched['brandID']);
                    $stmt1->execute();
                } else {
                    $stmt = $conn->prepare("INSERT INTO brands (brandID, brand, crcBrandURL) VALUES (null, :jsonbrand, :jsonbrandurl)");
                    $stmt->bindValue(":jsonbrand", array_search($jsonbrand, $jsonbrands));
                    $stmt->bindValue(":jsonbrandurl", $jsonbrand);
                    $stmt->execute();
                }
            }
        }
    }
}

foreach($prodfiles as $prodfile){
    $json = file_get_contents("../json/".$prodfile);
    $jsonprods = json_decode($json, true);
    foreach($jsonprods as $jsonbrands){
        foreach($jsonbrands as $jsonprod){
            if ($prodfile == "wiggleprodlist.json") {
                $stmt = $conn->prepare("INSERT INTO wiggleprods (prodname, produrl, prodpricegbp, prodpriceeur, brandID, retailer) VALUES (:jsonprodname, :jsonprodurl, :jsonprodpricegbp, :jsonprodpriceeur, :brandID, :retailer)");
                $stmt->bindValue(":retailer", "wiggle");
            } elseif ($prodfile == "bikediscountprodlist.json"){
                $stmt = $conn->prepare("INSERT INTO bdprods (prodname, produrl, prodpricegbp, prodpriceeur, brandID, retailer) VALUES (:jsonprodname, :jsonprodurl, :jsonprodpricegbp, :jsonprodpriceeur, :brandID, :retailer)");
                $stmt->bindValue(":retailer", "bikediscount");
            } elseif ($prodfile == "crcprodlist.json"){
                $stmt = $conn->prepare("INSERT INTO crcprods (prodname, produrl, prodpricegbp, prodpriceeur, brandID, retailer) VALUES (:jsonprodname, :jsonprodurl, :jsonprodpricegbp, :jsonprodpriceeur, :brandID, :retailer)");
                $stmt->bindValue(":retailer", "crc");
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
            $stmt1 = $conn->prepare("SELECT brandID FROM brands WHERE brand LIKE :brand");
            $stmt1->bindValue(":brand", array_search($jsonbrands, $jsonprods));
            if ($stmt1->execute()) {
                $brandID = $stmt1->fetch(PDO::FETCH_ASSOC)['brandID'];
            }
            $stmt->bindValue(":brandID", $brandID);
            $stmt->execute();
        }
    }
}

$conn = null;