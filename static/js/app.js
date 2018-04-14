$(function () {
  $('[data-toggle="tooltip"]').tooltip()
});

function criterions_mean(criterions){
    var sum = 0
    var nb = 0
    for(var propertyName in criterions) {

        if (criterions[propertyName] != "None") {
            sum += parseFloat(criterions[propertyName])
            nb += 1
        }
    }
    return sum / nb;
}

function update_score(){
    var criterions = [];
    $('.criterion_checkbox:checked').each(function(i){
      criterions.push($(this).val())
    });
    var mean = criterions_mean(criterions);
    $('#global_score').text(Math.round(mean * 100) / 100+' %')
}

$('.criterion_checkbox').on('change', function(){
    update_score();
});

$('#select_all_checkbox').on('click', function(){
    $('.criterion_checkbox').prop( "checked", true );
    update_score();
});


$('#deselect_all_checkbox').on('click', function(){
    $('.criterion_checkbox').prop( "checked", false );
    update_score();
});

