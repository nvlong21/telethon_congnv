<template>
  <div id="all-sess">
    <h1>All Sess</h1>

        <p><router-link :to="{ name: 'CreateSess' }" class="btn btn-primary">Create Sess</router-link></p>

        <div class="form-group">
            <input type="text" name="search" v-model="sessSearch" placeholder="Search sess" class="form-control" v-on:keyup="searchSesss">
        </div>

        <table class="table table-hover" style="width: 100%;">
            <thead>
            <tr>
                <td>ID</td>
                <td>Title</td>
                <td>Content</td>
                <td>Thumbnail</td>
                <td>Date Updated</td>
                <td>Date Created</td>
                <td>Actions</td>
            </tr>
            </thead>

            <tbody>
                <tr v-for="sess in sesss">
                    <td>{{ sess.id }}</td>
                    <td>{{ sess.title }}</td>
                    <td>{{ sess.content }}</td>
                    <td ><img :src="sess.thumbnail" width="50" height="50"/></td>
                    <td>{{ sess.date_updated }}</td>
                    <td>{{ sess.date_created }}</td>
                    <td>
                        <router-link :to="{name: 'EditSess', params: { id: sess.id }}" class="btn btn-primary">Edit</router-link>
                        <router-link :to="{name: 'DeleteSess', params: { id: sess.id }}" class="btn btn-danger">Delete</router-link>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script>
// import Punny from './Punny';

export default {
      data(){
          return{
              sesss: [],
              originalSesss: [],
              sessSearch: ''
          }
      },
      created: function()
      {
          this.fetchSessData();
      },
      methods: {
          fetchSessData: function()
          {
              this.$http.get('http://localhost:5000/sess').then((response) => {
                  this.sesss = response.body;
                  this.originalSesss = this.sesss;
                  for(var i = 0; i < this.sesss.length; i++) {
                      this.sesss[i].date_updated = new Date(this.sesss[i].date_updated).toString();
                      this.sesss[i].date_created = new Date(this.sesss[i].date_created).toString();
                  }
              }, (response) => {
              });
          },
          searchSesss: function()
          {
              if(this.sessSearch == '')
              {
                  this.sesss = this.originalSesss;
                  return;
              }
              var searchedSesss = [];
              for(var i = 0; i < this.originalSesss.length; i++)
              {
                  var sessTitle = this.originalSesss[i]['title'].toLowerCase();
                  if(sessTitle.indexOf(this.sessSearch.toLowerCase()) >= 0)
                  {
                      searchedSesss.push(this.originalSesss[i]);
                  }
              }
              this.sesss = searchedSesss;
          }
      }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  /*color: #42b983;*/
}
#all-sess {
    /*width: 400px;*/
    /*margin: 20px 20px 40px 40px;*/
    /*background-color: #66ffff;*/
    /*margin-top: 100px;
    margin-bottom: 100px;
    margin-right: 80px;
    margin-left: 80px;*/
}

</style>
