<!DOCTYPE html>
<html>
	<head>
		<meta charset="UTF-8" />
		<title>SegMeant</title>
		<link rel="stylesheet" href="scripts/treant/Treant.css" type="text/css"/>
		<link rel="stylesheet" href="style/style.css" />
		<script type="text/javascript" src="scripts/jquery-3.6.1.min.js"></script>
		<script src="scripts/xml2json.min.js"></script>
		<script src="scripts/jsonview/dist/jsonview.js"></script>
		<script src="scripts/json2table.js"></script>
		<script src="scripts/JSON5.min.js"></script>
		<script src="scripts/treant/vendor/raphael.js"></script>
		<script src="scripts/treant/Treant.js"></script>
		<script src="scripts/tree.js"></script>
        <script src="scripts/pagemap.min.js"></script>
		
	</head>
	
	<body>
		
		<div id="tabs" class="sidebar">
			<div class="tablinks">
				<button class="tabletab tablinks" id="tabletab">Table</button>
			</div>
			<div class="tablinks">
				<button class="treetab tablinks" id="treetab">Tree</button>
			</div>
            <input type="number" id="zoom" name="zoom" min="0.1" max="2.0" step="0.1" value="1.0">
		</div>
        <h2><a href="https://jerem-dy.github.io/SegMeantWeb/html/index.html">SegMeant</a></h2>
		<section class="viewarea">
			<div id="tabletab" class="tabcontent" hidden>
			</div>
			<div id="treetab" class="tabcontent" hidden>
				<div id="tree-simple" class="scrollable"></div>
			</div>
		</section>

		<canvas id='map'></canvas>
		<script type="text/javascript">

            pagemap(document.querySelector('#map'), {
                viewport: document.querySelector('.viewarea'),
                styles: {
                    'header,footer,section,article': 'rgba(0,0,0,0.08)',
                    'h1,a': 'rgba(0,0,0,0.10)',
                    'h2,h3,h4': 'rgba(0,0,0,0.08)'
                },
                back: 'rgba(0,0,0,0.02)',
                view: 'rgba(0,0,0,0.05)',
                drag: 'rgba(0,0,0,0.10)',
                interval: 50
            });

            $("#zoom").change(function(){
                $(".scrollable").css("scale", $("#zoom").val());
            });

			$("button.tablinks").on(
				{
					"click" : function()
					{

						let tabs = $(".tabcontent");
						let btns = $("button.tablinks");


						for(let i = 0 ; i < tabs.length ; i++)
						{
							if($(tabs[i]).attr('id') == $(this).attr('id'))
							{
								$(tabs[i]).show();
							}
							else
							{
								$(tabs[i]).hide();
							}
						}

						$(this).addClass("active");

						for(let i = 0 ; i < btns.length ; i++)
						{
							if(btns[i] != this)
							{
								$(btns[i]).removeClass("active");
							}
						}
					}
				}
			);


			$("button.toggleBtn").on(
				{
					"click" : function()
					{
						if($(this).hasClass("rightpannel"))
						{
							$("#ctrlTransport").toggle();
						}
						else if($(this).hasClass("lowpannel"))
						{
							$("#tabs").toggle();
						}
						
					}
					
				}
			);

            var down=false;
            var scrollLeft=0;
            var x = 0;

            $('.scrollable').mousedown(function(e) {
                down = true;
                scrollLeft = $('body').scrollLeft;
                x = e.clientX;
            }).mouseup(function() {
                down = false;
            }).mousemove(function(e) {
                if (down) {
                    $('body').scrollLeft = scrollLeft + x - e.clientX;
                }
            }).mouseleave(function() {
                down = false;
            });


					
            var result = <?php
                    putenv("LC_ALL=en_US.UTF-8");
                    $cmd = "python3 test.py "."\"".$_POST["text"]."\"";

                    exec($cmd, $return);

                    $xml_string = end($return);

                    print json_encode($xml_string);
                ?>;

            var doc = JSON5.parse(result);

            $(".tree").html("");
            
            var tree = create_chart(doc.tree, "#tree-simple");
            $('#tree-simple').css("overflow", "visible");

            let table = tableFromJson(doc.linear);

            table.classList.add('scrollable');

            document.querySelector("div#tabletab").appendChild(table)

			
		</script>
	</body>
</html>



