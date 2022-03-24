<template>
    <div id="delete-product">
        <h1>Delete Sess {{ sess.title }}</h1>

        <p><router-link :to="{ name: 'AllSess' }">Return to sesss</router-link></p>

        <notification v-bind:notifications="notifications"></notification>

        <form v-on:submit.prevent="deleteSess">
            <p><button class="btn btn-danger">Delete Sess</button></p>
        </form>
    </div>
</template>

<script>
    import Notification from './notifications.vue';

    export default{
        data(){
            return{
                sess:{},
                notifications:[]
            }
        },

        created: function(){
            this.getSess();
        },

        methods: {
            getSess: function()
            {
                this.$http.get('http://localhost:5000/sess/' + this.$route.params.id).then((response) => {
                    this.sess = response.body;
                }, (response) => {

                });
            },

            deleteSess: function()
            {
                if(this.notifications) this.notifications = [];
                this.$http.delete('http://localhost:5000/sess/' + this.$route.params.id, this.sess, {
                    headers : {
                        'Content-Type' : 'application/json'
                    }
                }).then((response) => {
                    this.$router.push({name: 'AllSess'})
                }, (response) => {
                    this.notifications.push({
                        type: 'danger',
                        message: 'Sess could not deleted'
                    });
                });
            }
        },

        components: {
            'notification' : Notification
        }
    }
</script>