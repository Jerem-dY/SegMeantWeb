<?php 

    /*if($_POST["rep1"] == "Paris" || $_POST["rep1"] == "paris" || $_POST["rep1"] == "PARIS"){
        print "<p>La capitale de la France est bien Paris.</p>";
    }
    else{
        print "<p>Eh non, la capitale de la France est Paris et non ". $_POST["rep1"] ." ! Ahah. </p>";
    }

    if($_POST["rep2"] == "Rome" || $_POST["rep2"] == "rome" || $_POST["rep2"] == "ROME"){
        print "<p>La capitale de l'Italie est bien Rome.</p>";
    }
    else{
        print "<p>Eh non, la capitale de l'Italie est Rome et non ". $_POST["rep2"] ." ! Ahah. </p>";
    }*/

    //print escapeshellarg(base64_encode('abé')); 

    //print base64_encode($_POST["text"]);
    putenv('LC_ALL=en_US.UTF-8');
    $cmd = "python3 test.py "."\"".$_POST["text"]."\"";

    //print mb_detect_encoding(htmlentities($cmd, ENT_COMPAT, 'UTF-8'));
    //print $cmd;
    $return = shell_exec($cmd);

    echo $return;

    $xml_string = simplexml_load_string(utf8_encode($return));

    print $xml_string;

    /*$document = new DOMDocument();
    $document->loadXML($xml_string);

    print $document->saveXML();*/

?>