<template>
    <div id="create-entrie">
        <h1>Create Sess</h1>

        <p><router-link :to="{ name: 'AllSess' }">Return to entries</router-link></p>

        <notification v-bind:notifications="notifications"></notification>
        <!-- <form> -->
        <form v-on:submit.prevent="addSess">

            <div class="form-group">
                <label name="mess_from">From</label>
                <input type="text" class="form-control" v-model="entrie.title" id="entrie_title" required>
            </div>
            <div class="form-group">
                <label name="entrie_content">Phone</label>
                <input type="text" class="form-control" v-model="entrie.phone" id="entrie_content" required>
            </div>
            <div class="form-group">
                <button class="btn btn-primary">Get code</button>
            </div>
        </form>
    </div>
</template>

<script>

import Notification from './notifications.vue';
export default{
    data(){
        return{
            entrie:{},
            notifications:[],
            image: '',
        }
    },
    methods: {
        addSess: function()
        {
            var formData = new FormData();
            formData.append('title', this.entrie.title);
            formData.append('phone', this.entrie.phone);
            if(this.notifications) this.notifications = [];
            this.$http.post('http://localhost:8000/add_entrie', formData, {
                headers : {
                    'enctype' : 'multipart/form-data'
                }
            }).then((response) => {
                if(response.data.status==1)
                {
                    this.notifications.push({
                        type: 'success',
                        message: 'Sess created successfully'
                    });
                    this.$router.push({name: 'VerifyCode', params:{"phone": this.entrie.phone}}); 
                }
                this.notifications.push({
                        type: 'error',
                        message: response.data.message
                    });
                // { name: 'user', params: { username: 'eduardo' } }
            }, (response) => {
                this.notifications.push({
                    type: 'error',
                    message: 'Sess not created'
                });
            });
        }
    },
    components: {
        'notification' : Notification
    }
}

</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
img {
  width: 30%;
  margin: auto;
  display: block;
  margin-bottom: 10px;
}
button {
  
}
</style>
