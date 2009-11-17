<?
if(!$_GET["debug"]) { header('Content-type: application/json'); } else { echo "<pre>\n"; }

$link = mysql_connect('localhost', 'wmbr', '40yitb');
$db_selected = mysql_select_db('wmbr', $link);

// I really don't want to have to do things this way!
// For historical reasons (maybe?) the times in the database
// are set up by "programming days" instead of by the
// actual times that the shows are on.
$dayclause = array(
  "Monday"    => "(((Shows.day = \"Monday\"    or Shows.day = \"Weekdays\") and Shows.time < \"24:00\") or ( Shows.day  = \"Sunday\"                                and Shows.time >= \"24:00\"))",
  "Tuesday"   => "(((Shows.day = \"Tuesday\"   or Shows.day = \"Weekdays\") and Shows.time < \"24:00\") or ((Shows.day = \"Monday\"    or Shows.day = \"Weekdays\") and Shows.time >= \"24:00\"))",
  "Wednesday" => "(((Shows.day = \"Wednesday\" or Shows.day = \"Weekdays\") and Shows.time < \"24:00\") or ((Shows.day = \"Tuesday\"   or Shows.day = \"Weekdays\") and Shows.time >= \"24:00\"))",
  "Thursday"  => "(((Shows.day = \"Thursday\"  or Shows.day = \"Weekdays\") and Shows.time < \"24:00\") or ((Shows.day = \"Wednesday\" or Shows.day = \"Weekdays\") and Shows.time >= \"24:00\"))",
  "Friday"    => "(((Shows.day = \"Friday\"    or Shows.day = \"Weekdays\") and Shows.time < \"24:00\") or ((Shows.day = \"Thursday\"  or Shows.day = \"Weekdays\") and Shows.time >= \"24:00\"))",
  "Saturday"  => "(( Shows.day = \"Saturday\"                               and Shows.time < \"24:00\") or ((Shows.day = \"Friday\"    or Shows.day = \"Weekdays\") and Shows.time >= \"24:00\"))",
  "Sunday"    => "(( Shows.day = \"Sunday\"                                 and Shows.time < \"24:00\") or ( Shows.day = \"Saturday\"                               and Shows.time >= \"24:00\"))"
);

// add signon and signoff events
$signonTable = array();
$signoffTable = array();
$query = "SELECT Shows1.showid as beforeid,Shows2.showid as afterid from Shows as Shows1, Shows as Shows2 where (Shows1.day = Shows2.day or (Shows1.day = \"Weekdays\" and (Shows2.day = \"Monday\" or Shows2.day = \"Tuesday\" or Shows2.day = \"Wednesday\" or Shows2.day = \"Thursday\" or Shows2.day = \"Friday\" or Shows2.day = \"Weekdays\")) or (Shows2.day = \"Weekdays\" and (Shows1.day = \"Monday\" or Shows1.day = \"Tuesday\" or Shows1.day = \"Wednesday\" or Shows1.day = \"Thursday\" or Shows1.day = \"Friday\"))) and addtime(Shows1.time,concat(floor(Shows1.length/60),\":\",Shows1.length%60)) = Shows2.time and Shows1.seasonid = Shows2.seasonid";
$result = mysql_query($query);
while($row = mysql_fetch_assoc($result)) {
  $signoffTable[$row["beforeid"]] = 1; // definitely don't have to sign off after this show
  $signonTable[$row["afterid"]] = 1; // definitely don't have to sign on before this show
}
mysql_free_result($result);

$rvalue = array();
for($i=0; $i<$_GET['num_days']; $i++) {
  $today = new DateTime(sprintf("%04d-%02d-%02d", $_GET['start_year'], $_GET['start_month'], $_GET['start_day']));
  $today -> modify(sprintf("+%d day", $i));
  $weekday = $today -> format ("l");
  $alternates = ($today -> format("W")) % 2 + 1;
  $today = $today -> format("Y-m-d");
  $rvalue[$today] = array();

// what is the current season
  $result = mysql_query(sprintf("SELECT seasonid from Seasons where (start <= '%s' and '%s' < end)", $today, $today));
  $row = mysql_fetch_assoc($result);
  $season = $row["seasonid"];
  mysql_free_result($result);
 
  $findMyBox = array();
// populate the shows
  $query = sprintf("SELECT Shows.showid,Shows.name,(HOUR(Shows.time)%%24) as hr,(MINUTE(Shows.time)) as min,Shows.length from Shows where Shows.seasonid=%d and %s and (Shows.alternates = 0 or Shows.alternates = %d) ORDER BY (hr*60+min)", $season, $dayclause[$weekday], $alternates);
  if($_GET["debug"]) {
    printf("%s\n", $query);
  }
  $result = mysql_query($query);
  while($row = mysql_fetch_assoc($result)) {
    $json_row = array();
    $json_row["start_time"] = sprintf("%02d:%02d", $row["hr"], $row["min"]);
    $endtime = $row["hr"]*60+$row["min"]+$row["length"];
    $json_row["end_time"]   = sprintf("%02d:%02d", ($endtime/60)%24, $endtime%60);
// fix the name
    $show_name              = $row["name"];
    $show_name              = str_replace("|",                  " ", $show_name);
    $show_name              = str_replace(array("~", "[", "]"), "",  $show_name);
    $json_row["show_name"]  = $show_name;
    $json_row["producers"]  = array();
    $json_row["announcers"] = array();
    $json_row["engineer"]   = "";
    $json_row["type"]       = "show";
    if($_GET["debug"]) {
      printf("%s--%s: %s\n", $json_row["start_time"], $json_row["end_time"], $json_row["show_name"]);
    }
    if(!array_key_exists($row["showid"], $signonTable)) {
      array_push($rvalue[$today], array("type" => "signon", "time" => $json_row["start_time"]));
    }
    $findMyBox[$row["showid"]] = array_push($rvalue[$today],$json_row)-1;
    if(!array_key_exists($row["showid"], $signoffTable)) {
      array_push($rvalue[$today], array("type" => "signoff", "time" => $json_row["end_time"]));
    }
  }
//  mysql_free_result($result);

// populate the staff
//  $result = mysql_query(sprintf("SELECT Shows.*,ShowStaff.* from Shows,ShowStaff where ShowStaff.showid=Shows.showid and Shows.seasonid=%d", $season));
  $query = sprintf("SELECT Shows.showid,Shows.day as sday,ShowStaff.day as ssday,CONCAT(Members.firstname,\" \",Members.middlename,\" \",Members.lastname,\" \",Members.suffix) as legalname,Members.publicname as djname,ShowStaff.producer,Members.ota_engineer from Shows,ShowStaff,Members where ShowStaff.showid=Shows.showid and ShowStaff.member_id=Members.member_id and Shows.seasonid=%d and %s and (Shows.alternates = 0 or Shows.alternates = %d) order by (sday != \"Weekdays\" or ssday = \"%s\") desc, Members.lastname", $season, $dayclause[$weekday], $alternates, $weekday);
  $result = mysql_query($query);
  while($row = mysql_fetch_assoc($result)) {
    $djname = trim(str_replace("  ", " ", utf8_encode($row["djname"])));
    $legalname = trim(str_replace("  ", " ", utf8_encode($row["legalname"])));
    if(strlen(trim($djname)) == 0) {
      $djname = $legalname;
    }
    if($row["producer"] == "y") {
      array_push($rvalue[$today][$findMyBox[$row["showid"]]]["producers"],  $djname);
    }
    array_push($rvalue[$today][$findMyBox[$row["showid"]]]["announcers"], $djname);
    if(strlen($rvalue[$today][$findMyBox[$row["showid"]]]["engineer"]) == 0 && $row["ota_engineer"] == "y") {
      $rvalue[$today][$findMyBox[$row["showid"]]]["engineer"] = $legalname;
    }
  }
  mysql_free_result($result);
}
if($_GET["debug"]) {
  print_r($rvalue);
} else {
  print json_encode($rvalue);
}
?>
