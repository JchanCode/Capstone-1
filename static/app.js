
///////////////////////////////////////////////////////////////////////////////////
// 
//                                    Card
//  
// 
///////////////////////////////////////////////////////////////////////////////////


// Watchlist card
$(document).ready(function(){
    $("#watchlist-tab").click(async function(e){
        e.preventDefault();
        watchlists = await getWatchlist()
        $("#watchlist").empty();
        let $ol = $('<ol></ol>');
        for (stock of watchlists ) {
          $(`<li><a href="/stocks/${stock.symbol}">${stock.symbol}</a></li>`).appendTo($ol)
        };
        $ol.appendTo($('#watchlist'))
        $(this).tab('show');
    });
});


// Following Card
$(document).ready(function(){
    $("#following-tab").click(async function(e){
        e.preventDefault();
        followings = await getFollowing()
        $("#following").empty();
        let $ol = $('<ol></ol>');
        for (user of followings ) {
          $(`<li><a href="/users/${user.id}">${user.username}</a></li>`).appendTo($ol)
        };
        $ol.appendTo($('#following'))
        $(this).tab('show');
    });
});


//  Liked Card
$(document).ready(function(){
    $("#likes-tab").click(async function(e){
        e.preventDefault(); 
        likes = await getLikes()
        $("#likes").empty();
        let $ol = $('<ol></ol>');
        for (like of likes ) {
          $(`<li><a href="/chatters/${like.id}">${like.title}</a></li>`).appendTo($ol)
        };
        $ol.appendTo($('#likes'))
        $(this).tab('show');
    });
});

///////////////////////////////////////////////////////////////////////////////////
// 
//                                profile.html
//  
// 
///////////////////////////////////////////////////////////////////////////////////


// profile watchlist
$(document).ready(function(){
    $("#watchlist-profTab").click(async function(e){
        e.preventDefault();
        watchlists = await getWatchlist()
        $("#prof-watchlist").empty();
        
        const $table = $(`<table class="table">
                            <thead>
                              <tr>
                                <th scope="col">Symbol</th>
                                <th scope="col">Name</th>
                                <th scope="col">Exchange</th>
                                <th scope="col">Industry</th>
                                <th scope="col">52WeekHigh</th>
                                <th scope="col">52WeekLow</th>
                              </tr>
                            </thead>
                            <tbody class="prof-watchlist-content">
                            </tbody>
                          </table>`);
        $table.appendTo($("#prof-watchlist"));
        for (stock of watchlists) {
            $(`<tr>
                <th scope="row">${stock.symbol}</th>
                <th><a href="/stocks/${stock.symbol}">${stock.name}</th>
                <th>${stock.exchange}</th>
                <th>${stock.industry}</th>
                <th class="text-success">${stock.weekhigh}<i class="fas fa-sort-up"></i></th>
                <th class="text-danger">${stock.weeklow}<i class="fas fa-sort-down"></i></th>
               </tr>`).appendTo($(".prof-watchlist-content"))
        };
        $(this).tab('show');
    });
});


// profile chatter
$(document).ready(function(){
    $("#chatters-profTab").click(async function(e){
        e.preventDefault();

        chatters = await getChatters();
        $("#prof-followers").empty();
        const $li = $("<ul id='chatter' class='list-group list-group-flush'></ul>")
        $li.appendTo($("#prof-chatters"))
        for ( chatter of chatters ) {

          $(`<li class="list-group-item d-flex ">
          <p > <a href="/chatters/${chatter.id}">${chatter.title}</a><small class="m-1">${chatter.timestamp}</small></p>
          <span class="m-1"><i class="far fa-comment-alt">${chatter.c_length}</i></span>
          </li>`).appendTo($("#chatter"))
        }

        $(this).tab('show');
    });
});


// profile followers 
$(document).ready(function(){
    $("#followers-profTab").click(async function(e){
        e.preventDefault();
        followers = await getFollower();
        $("#prof-followers").empty();
        const $ul = $("<ul class='list-unstyled follower-content'></ul>");
        $ul.appendTo("#prof-followers");
        for ( follower of followers ) {
          $(` <li class="media">
                <div class="media-left">
                    <img class="media-object mr-3 chatter-img" src="${follower.image_url}" alt="${follower.username}'s image">
                </div>
                <div class="media-body">
                    <h5 class="media-heading mt-0 mb-1"><a href="/users/${follower.id}">${follower.username}</a></h5>
                    <i class="fa fa-map-marker location-marker" > ${follower.location}</i>
                </div>
              </li>`).appendTo($(".follower-content"))
        };
        $(this).tab('show');
    });
});


// profile following
$(document).ready(function(){
    $("#following-profTab").click(async function(e){
        e.preventDefault();
        followings = await getFollowing();
        $("#prof-following").empty();
        const $ul = $("<ul class='list-unstyled following-content'></ul>");
        $ul.appendTo("#prof-following");
        for ( following of followings ) {
          $(` <li class="media">
                <div class="media-left">
                    <img class="media-object mr-3 chatter-img" src="${following.image_url}" alt="${following.username}'s image">
                </div>
                <div class="media-body">
                    <h5 class="media-heading mt-0 mb-1"><a href="/users/${following.id}">${following.username}</a></h5>
                    <i class="fa fa-map-marker location-marker" > ${following.location}</i>
                </div>
              </li>`).appendTo($(".following-content"))
        };
        $(this).tab('show');
    });
});


// profile likes
$(document).ready(function(){
    $("#likes-profTab").click(async function(e){
        e.preventDefault();

        likes = await getLikes();
        $("#prof-likes").empty();
        const $li = $("<ul id='likes' class='list-group list-group-flush'></ul>")
        $li.appendTo($("#prof-likes"))
        for ( like of likes ) {

          $(`<li class="list-group-item d-flex ">
          <p > <a href="/chatters/${like.id}">${like.title}</a><small class="m-1">${like.timestamp}</small></p>
          <span class="m-1"><i class="far fa-comment-alt">${like.c_length}</i></span>
          </li>`).appendTo($("#likes"))
        }

        $(this).tab('show');
    });
});
///////////////////////////////////////////////////////////////////////////////////
// 
//                                helper function
//  
// 
///////////////////////////////////////////////////////////////////////////////////


async function getWatchlist() {
  const watchlists = await axios.get("http://127.0.0.1:5000/api/watchlist");
  return watchlists.data;
}


async function getFollowing() {
  const followings = await axios.get("http://127.0.0.1:5000/api/following");
  return followings.data;
}


async function getLikes() {
  const likes = await axios.get("http://127.0.0.1:5000/api/like")
  return likes.data;
}

async function getChatters() {
  const chatters = await axios.get("http://127.0.0.1:5000/api/chatter")
  return chatters.data;
}

async function getFollower() {

  const followers = await axios.get("http://127.0.0.1:5000/api/follower");
  return followers.data;
  
}