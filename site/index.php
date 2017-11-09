<?php
error_reporting(-1);
ini_set("display_errors", 1);
require('vendor/autoload.php');
require('inc/util.inc.php');
require('inc/config.inc.php');

require('inc/session.inc.php');

if (!isset($_GET['sentence']) || !$_GET['sentence']) {
	die('ERROR: sentence parameter must be given');
}

if (strlen($_GET['sentence']) > 1024) {
	die('ERROR: sentence too long. Only 1024 bytes allowed.');
}

$sentence = $_GET['sentence'];

try {
	$response = Requests::get("$api/sentences/" . rawurlencode($sentence) . "/auto");
} catch (Requests_Exception $e) {
	die('ERROR: could not connect to REST server. Is it running?');
}

if (!$response->success) {
	die('ERROR: bad API response status');
}

$parser_parse = $response->body;

if ($is_user_logged_in) {
	try {
		$response = Requests::get("$api/sentences/" . rawurlencode($sentence) . "/" . $user_name);
	} catch (Requests_Exception $e) {
		die('ERROR: could not connect to REST server. Is it running?');
	}
	
	if (!$response->success) {
		die('ERROR: bad API response status');
	}
	
	$user_parse = $response->body;
}
?>
<!DOCTYPE html>
<html>
	<head>
		<meta charset="UTF-8">
		<meta http-equiv="X-UA-Compatible" content="IE=edge">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<title>CCGWeb</title>

		<!-- Bootstrap styles -->
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">

		<!-- Our styles -->
		<link rel=stylesheet href=css/main.css>
		<link rel=stylesheet href=css/der.css>
	</head>
	<body>
		<?php require('inc/navbar.inc.php'); ?>
		<main>
			<h2>Sentence</h2>

			<p><?= htmlspecialchars($sentence); ?></p>

			<h2>Parse</h2>

			<ul class="nav nav-tabs">
				<li class="<?= $is_user_logged_in ? '' : 'active' ?>"><a data-toggle=tab href=#parses_parser>Parser</a></li>
				<?php if ($is_user_logged_in) { ?>
					<li class=active><a data-toggle=tab href=#parses_mine>Mine</a></li>
				<?php } ?>
			</ul>
			<div class=tab-content>
				<div id=parses_parser class="tab-pane <?= $is_user_logged_in ? '' : 'active' ?>">
					<?= xslTransform('xsl/der.xsl', $parser_parse) ?>
				</div>
				<?php if ($is_user_logged_in) { ?>
					<div id=parses_mine class="tab-pane active">
						<?= xslTransform('xsl/der.xsl', $user_parse) ?>
					</div>
				<?php } ?>
			</div>
		</main>

		<!-- jQuery -->
		<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>

		<!-- Bootstrap scripts -->
		<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>

		<!-- Our scripts -->
		<script>
<?php
echo "const api = " .json_encode($api) . "\n";

if ($is_user_logged_in) {
	echo "const isUserLoggedIn = true\n";
	echo "const userName = ". json_encode($user_name) . "\n";
} else {
	echo "const isUserLoggedIn = false\n";
}

echo "const sentence = " . json_encode($sentence) . "\n";
?>
		</script>
		<script src=js/der.js></script>
	</body>
</html>
