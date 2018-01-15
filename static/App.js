
$(function(){

	$(".prod-name").click(function(e){
		var $clicked = $(this).attr('id')
		var ndb = $clicked
		$.ajax({
			type: "POST",
			url: "/get_ingredients",
			data: JSON.stringify(ndb),
			contentType: 'application/json',
			dataType: 'json',
			success: function(data){
				$('#ingredient-list').html((data.search_ndbno['report']['food']['ing']['desc']));

				$('#additive-list').html('');

				var allAdditives = data.additives;
				
				var addInfo = data.additive_information;

				var description = "description";


				for(var key in addInfo){
					$('#additive-list').append('<li>'+'<a tabindex="0" data-toggle="popover" data-trigger="focus" data-html="true" title="' + key + '" data-content="' + '<strong>Description</strong>:<br>' + (addInfo[key]["description"]) + '<hr>' + '<strong>Uses</strong>:<br>' + (addInfo[key]["uses"]) + '<hr>' + '<strong>Toxicity</strong>:<br>' + (addInfo[key]["toxicity"]) + '">' + key + '</a></li>');
					$('[data-toggle="popover"]').popover();
				}
			}
		})
	})

	$('.prod-name').click(function(){
		$('.selected').removeClass('selected');
		$(this).addClass('selected');
	})

	 
});